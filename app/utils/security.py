#  Copyright (c) 2017-2026 null. All rights reserved.
"""安全中间件模块，提供IP过滤、速率限制、CSRF防护等安全功能"""
import secrets
import time
from typing import Dict, List, Optional, Tuple

from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import settings
from app.utils.logger import logger
from app.utils.request import get_client_ip


def _validate_headers(request: Request) -> bool:
    """
    校验请求头合法性

    :param request: FastAPI 请求对象
    :return: 请求头是否合法
    """
    user_agent = request.headers.get("User-Agent")
    if not user_agent:
        return False

    if request.method not in ("GET", "HEAD", "OPTIONS"):
        content_type = request.headers.get("Content-Type")
        if not content_type or not (
                "multipart/form-data" in content_type
                or "application/json" in content_type
                or "application/x-www-form-urlencoded" in content_type
        ):
            return False

    return True


async def _validate_csrf_token(request: Request, csrf_tokens: Dict[str, Tuple[str, float]]) -> bool:
    """
    验证CSRF token有效性

    :param request: FastAPI 请求对象
    :param csrf_tokens: 存储的CSRF token字典 {client_ip: (token, expiry)}
    :return: token是否有效
    """
    token = request.headers.get("X-CSRF-Token")
    if not token:
        try:
            form_data = await request.form()
            token = form_data.get("csrf_token")
        except Exception:
            logger.debug("从form数据获取CSRF token失败，请求URL: %s", request.url.path)
            pass

    cookie_token = request.cookies.get("csrf_token")
    if not token or not cookie_token:
        return False

    client_ip = get_client_ip(request)
    if client_ip in csrf_tokens:
        stored_token, expiry = csrf_tokens[client_ip]
        if token == stored_token and time.time() < expiry:
            return True

    return False


class SecurityMiddleware(BaseHTTPMiddleware):
    """安全中间件，负责IP过滤、速率限制和CSRF防护"""

    _instance: Optional["SecurityMiddleware"] = None

    def __init__(self, app):
        super().__init__(app)
        self.allowed_ips: List[str] = settings.allowed_ips_list
        self.blocked_ips: List[str] = settings.blocked_ips_list
        self.rate_limit_per_ip: int = settings.RATE_LIMIT_PER_IP
        self.rate_limit_window: int = settings.RATE_LIMIT_WINDOW
        self.csrf_token_expiry: int = settings.CSRF_TOKEN_EXPIRY
        self.ip_requests: Dict[str, List[float]] = {}
        self.csrf_tokens: Dict[str, Tuple[str, float]] = {}
        SecurityMiddleware._instance = self

    async def dispatch(self, request: Request, call_next):
        client_ip = get_client_ip(request)

        if client_ip in self.blocked_ips:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="您的IP已被禁止访问",
            )

        if self.allowed_ips and client_ip not in self.allowed_ips:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="您的IP不在允许访问的范围内",
            )

        if not self._check_rate_limit(client_ip):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="请求过于频繁，请稍后再试",
            )

        if not _validate_headers(request):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="请求头校验失败",
            )

        if request.method not in ("GET", "HEAD", "OPTIONS"):
            if not await _validate_csrf_token(request, self.csrf_tokens):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="CSRF token验证失败",
                )

        response = await call_next(request)

        if request.method == "GET":
            self._clean_expired_csrf_tokens()
            token = self.get_csrf_token(client_ip)
            response.set_cookie(
                key="csrf_token",
                value=token,
                httponly=True,
                secure=settings.SECURE_COOKIE,
                samesite="lax",
                max_age=self.csrf_token_expiry,
            )

        return response

    def _check_rate_limit(self, client_ip: str) -> bool:
        """
        检查指定IP的请求速率是否超限

        :param client_ip: 客户端IP地址
        :return: 是否在速率限制范围内
        """
        current_time = time.time()
        if client_ip in self.ip_requests:
            self.ip_requests[client_ip] = [
                t for t in self.ip_requests[client_ip]
                if current_time - t < self.rate_limit_window
            ]
        else:
            self.ip_requests[client_ip] = []

        if len(self.ip_requests[client_ip]) >= self.rate_limit_per_ip:
            return False

        self.ip_requests[client_ip].append(current_time)
        return True

    def _generate_csrf_token(self, client_ip: str) -> str:
        """
        为指定IP生成新的CSRF token

        :param client_ip: 客户端IP地址
        :return: 生成的CSRF token
        """
        token = secrets.token_hex(32)
        expiry = time.time() + self.csrf_token_expiry
        self.csrf_tokens[client_ip] = (token, expiry)
        return token

    def _clean_expired_csrf_tokens(self):
        """清理过期的CSRF token"""
        current_time = time.time()
        expired_ips = [
            ip for ip, (_, expiry) in self.csrf_tokens.items()
            if current_time >= expiry
        ]
        for ip in expired_ips:
            del self.csrf_tokens[ip]

    def get_csrf_token(self, client_ip: str) -> str:
        """
        获取当前CSRF token，如果不存在或已过期则生成新的

        :param client_ip: 客户端IP地址
        :return: 有效的CSRF token
        """
        current_time = time.time()
        if client_ip not in self.csrf_tokens or current_time >= self.csrf_tokens[client_ip][1]:
            return self._generate_csrf_token(client_ip)
        return self.csrf_tokens[client_ip][0]

    @classmethod
    def get_instance(cls) -> Optional["SecurityMiddleware"]:
        """
        获取中间件单例实例

        :return: SecurityMiddleware 实例，未初始化时返回 None
        """
        return cls._instance


__all__ = ["SecurityMiddleware"]
