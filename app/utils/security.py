#  Copyright (c) 2017-2026 null. All rights reserved.
import os
import secrets
import time
from typing import Dict, List, Optional, Tuple

from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware


def _get_client_ip(request: Request) -> str:
    """获取客户端IP"""
    x_forwarded_for = request.headers.get("X-Forwarded-For")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()
    return request.client.host


def _validate_headers(request: Request) -> bool:
    """校验请求头"""
    # 检查User-Agent
    user_agent = request.headers.get("User-Agent")
    if not user_agent:
        return False

    # 检查Content-Type（对于非GET请求）
    if request.method not in ["GET", "HEAD", "OPTIONS"]:
        content_type = request.headers.get("Content-Type")
        if not content_type or not ("multipart/form-data" in content_type or "application/json" in content_type or "application/x-www-form-urlencoded" in content_type):
            return False

    return True


async def _validate_csrf_token(request: Request, csrf_tokens: Dict[str, Tuple[str, float]]) -> bool:
    """验证CSRF token"""
    # 从请求头或表单中获取token
    token = request.headers.get("X-CSRF-Token")
    if not token:
        # 尝试从表单中获取
        try:
            form_data = await request.form()
            token = form_data.get("csrf_token")
        except Exception:
            pass

    # 从cookie中获取token进行比较
    cookie_token = request.cookies.get("csrf_token")

    if not token or not cookie_token:
        return False

    # 验证token是否匹配且未过期
    client_ip = _get_client_ip(request)
    if client_ip in csrf_tokens:
        stored_token, expiry = csrf_tokens[client_ip]
        if token == stored_token and time.time() < expiry:
            return True

    return False


class SecurityMiddleware(BaseHTTPMiddleware):
    """安全中间件"""

    # 类变量，存储中间件实例
    _instance = None

    def __init__(self, app,
                 allowed_ips: Optional[List[str]] = None,
                 blocked_ips: Optional[List[str]] = None,
                 rate_limit_per_ip: int = 5,
                 rate_limit_window: int = 1,
                 csrf_token_expiry: int = 3600):
        super().__init__(app)
        self.allowed_ips = allowed_ips or []
        self.blocked_ips = blocked_ips or []
        self.rate_limit_per_ip = rate_limit_per_ip
        self.rate_limit_window = rate_limit_window  # 单位：秒
        self.csrf_token_expiry = csrf_token_expiry  # CSRF token过期时间（秒）
        self.ip_requests: Dict[str, List[float]] = {}  # 记录每个IP的请求时间
        self.csrf_tokens: Dict[str, Tuple[str, float]] = {}  # 存储CSRF token和过期时间
        SecurityMiddleware._instance = self  # 保存实例引用

    async def dispatch(self, request: Request, call_next):
        """处理请求"""
        # 1. 获取客户端IP
        client_ip = _get_client_ip(request)

        # 2. IP黑名单检查
        if client_ip in self.blocked_ips:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="您的IP已被禁止访问"
            )

        # 3. IP白名单检查（如果设置了白名单）
        if self.allowed_ips and client_ip not in self.allowed_ips:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="您的IP不在允许访问的范围内"
            )

        # 4. 速率限制检查
        if not self._check_rate_limit(client_ip):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="请求过于频繁，请稍后再试"
            )

        # 5. 请求头校验
        if not _validate_headers(request):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="请求头校验失败"
            )

        # 6. 防CSRF攻击检查（对于非GET请求）
        if request.method not in ["GET", "HEAD", "OPTIONS"]:
            if not await _validate_csrf_token(request, self.csrf_tokens):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="CSRF token验证失败"
                )

        # 处理请求
        response = await call_next(request)

        # 为响应添加CSRF token
        if request.method == "GET":
            # 清理过期的CSRF token
            self._clean_expired_csrf_tokens()
            
            # 生成或更新CSRF token
            token = self.get_csrf_token(client_ip)

            # 设置cookie
            secure = os.environ.get("SECURE_COOKIE", "True").lower() == "true"
            response.set_cookie(
                key="csrf_token",
                value=token,
                httponly=True,
                secure=secure,  # 生产环境应设置为True
                samesite="lax",
                max_age=self.csrf_token_expiry
            )

        return response

    def _check_rate_limit(self, client_ip: str) -> bool:
        """检查速率限制"""
        current_time = time.time()

        # 清理过期的请求记录
        if client_ip in self.ip_requests:
            self.ip_requests[client_ip] = [
                t for t in self.ip_requests[client_ip]
                if current_time - t < self.rate_limit_window
            ]
        else:
            self.ip_requests[client_ip] = []

        # 检查是否超过限制
        if len(self.ip_requests[client_ip]) >= self.rate_limit_per_ip:
            return False

        # 记录本次请求
        self.ip_requests[client_ip].append(current_time)
        return True

    def _generate_csrf_token(self, client_ip: str) -> str:
        """生成CSRF token"""
        token = secrets.token_hex(32)
        expiry = time.time() + self.csrf_token_expiry
        self.csrf_tokens[client_ip] = (token, expiry)
        return token

    def _clean_expired_csrf_tokens(self):
        """清理过期的CSRF token"""
        current_time = time.time()
        expired_ips = [ip for ip, (_, expiry) in self.csrf_tokens.items() if current_time >= expiry]
        for ip in expired_ips:
            del self.csrf_tokens[ip]

    def get_csrf_token(self, client_ip: str) -> str:
        """获取当前CSRF token，如果不存在或已过期则生成新的"""
        current_time = time.time()
        if client_ip not in self.csrf_tokens or current_time >= self.csrf_tokens[client_ip][1]:
            return self._generate_csrf_token(client_ip)
        return self.csrf_tokens[client_ip][0]

    @classmethod
    def get_instance(cls) -> Optional['SecurityMiddleware']:
        """获取中间件实例"""
        return cls._instance


# 安全配置
SECURITY_CONFIG = {
    "allowed_ips": [ip.strip() for ip in os.environ.get("ALLOWED_IPS", "").split(",") if ip.strip()],  # 从环境变量读取允许的IP
    "blocked_ips": [ip.strip() for ip in os.environ.get("BLOCKED_IPS", "").split(",") if ip.strip()],  # 从环境变量读取禁止的IP
    "rate_limit_per_ip": int(os.environ.get("RATE_LIMIT_PER_IP", "5")),  # 从环境变量读取速率限制
    "rate_limit_window": int(os.environ.get("RATE_LIMIT_WINDOW", "1")),  # 从环境变量读取时间窗口
    "csrf_token_expiry": int(os.environ.get("CSRF_TOKEN_EXPIRY", "3600"))  # CSRF token过期时间（秒）
}


def get_security_middleware():
    """获取安全中间件实例"""
    return SecurityMiddleware(
        allowed_ips=SECURITY_CONFIG["allowed_ips"],
        blocked_ips=SECURITY_CONFIG["blocked_ips"],
        rate_limit_per_ip=SECURITY_CONFIG["rate_limit_per_ip"],
        rate_limit_window=SECURITY_CONFIG["rate_limit_window"],
        csrf_token_expiry=SECURITY_CONFIG["csrf_token_expiry"]
    )


__all__ = ["SecurityMiddleware", "get_security_middleware", "SECURITY_CONFIG"]