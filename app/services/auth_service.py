#  Copyright (c) 2017-2026 null. All rights reserved.
"""认证服务模块，处理CSRF Token和会话信息等业务逻辑"""
import secrets

from app.utils.logger import logger
from app.utils.request import get_client_ip
from app.utils.security import SecurityMiddleware


class AuthService:
    """认证服务，负责CSRF Token管理和会话信息获取"""

    @staticmethod
    def get_csrf_token(request) -> str:
        """
        获取当前会话的CSRF Token

        :param request: FastAPI 请求对象
        :return: CSRF Token 字符串
        """
        client_ip = get_client_ip(request)
        security_middleware = SecurityMiddleware.get_instance()

        if security_middleware:
            token = security_middleware.get_csrf_token(client_ip)
        else:
            token = secrets.token_hex(32)

        logger.info("CSRF Token获取成功，客户端IP: %s", client_ip)
        return token

    @staticmethod
    def get_session_info(request) -> dict:
        """
        获取当前会话的基本信息

        :param request: FastAPI 请求对象
        :return: 会话信息字典
        """
        client_ip = get_client_ip(request)
        security_middleware = SecurityMiddleware.get_instance()

        session_info = {
            "client_ip": client_ip,
            "has_csrf_token": False,
            "csrf_token": None,
        }

        if security_middleware and client_ip in security_middleware.csrf_tokens:
            session_info["has_csrf_token"] = True
            session_info["csrf_token"] = security_middleware.csrf_tokens[client_ip][0]

        logger.info("会话信息获取成功，客户端IP: %s", client_ip)
        return session_info
