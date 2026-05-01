#  Copyright (c) 2017-2026 null. All rights reserved.
"""认证相关的Pydantic模式定义"""
from pydantic import BaseModel


class CSRFTokenResponse(BaseModel):
    """CSRF Token响应模式"""
    code: int
    csrf_token: str
    message: str


class SessionInfoResponse(BaseModel):
    """会话信息响应模式"""
    code: int
    data: dict
    message: str
