#  Copyright (c) 2017-2026 null. All rights reserved.
from slowapi import Limiter
from slowapi.util import get_remote_address

# 创建限流对象，限制并发不超过10
limiter = Limiter(key_func=get_remote_address, default_limits=["10/second"])

# 导出limiter
__all__ = ["limiter"]
