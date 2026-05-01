#  Copyright (c) 2017-2026 null. All rights reserved.
"""认证API端点，提供CSRF Token获取和会话信息查询"""
from fastapi import APIRouter, Request

from app.schemas.auth import CSRFTokenResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["认证"])


@router.get(
    "/csrf-token",
    response_model=CSRFTokenResponse,
    summary="获取CSRF Token",
    description="获取当前会话的CSRF Token，用于后续需要CSRF验证的请求",
)
async def get_csrf_token(request: Request):
    token = AuthService.get_csrf_token(request)
    return CSRFTokenResponse(
        code=200,
        csrf_token=token,
        message="CSRF token获取成功",
    )


@router.get(
    "/session-info",
    summary="获取会话信息",
    description="获取当前会话的基本信息，包括客户端IP和CSRF Token状态",
)
async def get_session_info(request: Request):
    session_info = AuthService.get_session_info(request)
    return {
        "code": 200,
        "data": session_info,
        "message": "会话信息获取成功",
    }
