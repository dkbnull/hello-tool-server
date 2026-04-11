#  Copyright (c) 2017-2026 null. All rights reserved.
from fastapi import Request


def get_client_ip(request: Request) -> str:
    """获取客户端真实IP地址"""
    x_forwarded_for = request.headers.get("X-Forwarded-For")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()
    return request.client.host
