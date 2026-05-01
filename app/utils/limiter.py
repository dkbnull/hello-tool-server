#  Copyright (c) 2017-2026 null. All rights reserved.
"""限流模块，基于 slowapi 提供请求速率限制"""
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address, default_limits=["10/second"])

__all__ = ["limiter"]
