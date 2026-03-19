#  Copyright (c) 2017-2026 null. All rights reserved.
from fastapi import APIRouter, Request
from pydantic import BaseModel

from app.utils.security import _get_client_ip, SecurityMiddleware

router = APIRouter(prefix="/auth", tags=["认证"])


class CSRFTokenResponse(BaseModel):
    """CSRF token响应模型"""
    code: int
    csrf_token: str
    message: str


@router.get("/csrf-token", response_model=CSRFTokenResponse, summary="获取CSRF token")
async def get_csrf_token(request: Request):
    """获取当前会话的CSRF token
    
    该接口用于获取当前会话的CSRF token，用于后续需要CSRF验证的请求。
    如果当前会话已存在token，则返回现有token；否则生成新的token。
    """
    client_ip = _get_client_ip(request)

    # 获取安全中间件实例
    security_middleware = SecurityMiddleware.get_instance()

    if security_middleware:
        # 获取或生成CSRF token
        token = security_middleware.get_csrf_token(client_ip)
    else:
        # 如果无法获取中间件实例，生成新的token
        import secrets
        token = secrets.token_hex(32)

    return CSRFTokenResponse(
        code=200,
        csrf_token=token,
        message="CSRF token获取成功"
    )


@router.get("/session-info", summary="获取会话信息")
async def get_session_info(request: Request):
    """获取当前会话的基本信息"""
    client_ip = _get_client_ip(request)

    # 获取安全中间件实例
    security_middleware = SecurityMiddleware.get_instance()

    session_info = {
        "client_ip": client_ip,
        "has_csrf_token": False,
        "csrf_token": None
    }

    if security_middleware and client_ip in security_middleware.csrf_tokens:
        session_info["has_csrf_token"] = True
        session_info["csrf_token"] = security_middleware.csrf_tokens[client_ip]

    return {
        "code": 200,
        "data": session_info,
        "message": "会话信息获取成功"
    }
