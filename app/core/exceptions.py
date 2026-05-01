#  Copyright (c) 2017-2026 null. All rights reserved.
"""自定义异常模块，建立层次化的异常体系"""
from fastapi import status


class AppException(Exception):
    """应用基础异常，所有自定义异常的父类"""

    def __init__(self, message: str = "服务内部错误", code: int = -1,
                 status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR):
        self.message = message
        self.code = code
        self.status_code = status_code
        super().__init__(self.message)


class NotFoundException(AppException):
    """资源未找到异常"""

    def __init__(self, message: str = "资源不存在", code: int = -1):
        super().__init__(message=message, code=code, status_code=status.HTTP_404_NOT_FOUND)


class ValidationError(AppException):
    """请求参数校验异常"""

    def __init__(self, message: str = "请求参数校验失败", code: int = -1):
        super().__init__(message=message, code=code, status_code=status.HTTP_400_BAD_REQUEST)


class BusinessException(AppException):
    """业务逻辑异常"""

    def __init__(self, message: str = "业务处理失败", code: int = -1,
                 status_code: int = status.HTTP_422_UNPROCESSABLE_ENTITY):
        super().__init__(message=message, code=code, status_code=status_code)


class RateLimitExceededException(AppException):
    """请求频率超限异常"""

    def __init__(self, message: str = "请求过于频繁，请稍后再试", code: int = -1):
        super().__init__(message=message, code=code, status_code=status.HTTP_429_TOO_MANY_REQUESTS)


class ForbiddenException(AppException):
    """禁止访问异常"""

    def __init__(self, message: str = "禁止访问", code: int = -1):
        super().__init__(message=message, code=code, status_code=status.HTTP_403_FORBIDDEN)
