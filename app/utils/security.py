#  Copyright (c) 2017-2026 null. All rights reserved.
import os
import secrets
import time
from typing import Dict, List, Optional, Tuple

from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import SECURITY_CONFIG
from app.utils.request import get_client_ip


def _validate_headers(request: Request) -> bool:
    """校验请求头"""
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
    """验证CSRF token"""
    token = request.headers.get("X-CSRF-Token")
    if not token:
        try:
            form_data = await request.form()
            token = form_data.get("csrf_token")
        except Exception:
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
    """安全中间件"""

    _instance: Optional["SecurityMiddleware"] = None

    def __init__(
            self,
            app,
            allowed_ips: Optional[List[str]] = None,
            blocked_ips: Optional[List[str]] = None,
            rate_limit_per_ip: int = 5,
            rate_limit_window: int = 1,
            csrf_token_expiry: int = 3600,
    ):
        super().__init__(app)
        self.allowed_ips = allowed_ips or []
        self.blocked_ips = blocked_ips or []
        self.rate_limit_per_ip = rate_limit_per_ip
        self.rate_limit_window = rate_limit_window
        self.csrf_token_expiry = csrf_token_expiry
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
            secure = os.environ.get("SECURE_COOKIE", "True").lower() == "true"
            response.set_cookie(
                key="csrf_token",
                value=token,
                httponly=True,
                secure=secure,
                samesite="lax",
                max_age=self.csrf_token_expiry,
            )

        return response

    def _check_rate_limit(self, client_ip: str) -> bool:
        """检查速率限制"""
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
        """生成CSRF token"""
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
        """获取当前CSRF token，如果不存在或已过期则生成新的"""
        current_time = time.time()
        if client_ip not in self.csrf_tokens or current_time >= self.csrf_tokens[client_ip][1]:
            return self._generate_csrf_token(client_ip)
        return self.csrf_tokens[client_ip][0]

    @classmethod
    def get_instance(cls) -> Optional["SecurityMiddleware"]:
        """获取中间件实例"""
        return cls._instance


__all__ = ["SecurityMiddleware", "SECURITY_CONFIG"]
