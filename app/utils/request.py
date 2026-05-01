#  Copyright (c) 2017-2026 null. All rights reserved.
"""请求工具模块，提供客户端IP获取等请求相关功能"""
from fastapi import Request


def get_client_ip(request: Request) -> str:
    """
    获取客户端真实IP地址

    :param request: FastAPI 请求对象
    :return: 客户端IP地址
    """
    x_forwarded_for = request.headers.get("X-Forwarded-For")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()
    return request.client.host
