#  Copyright (c) 2017-2026 null. All rights reserved.
"""文件转换相关的Pydantic模式定义"""
from pydantic import BaseModel


class ConvertResponse(BaseModel):
    """文件转换响应模式"""
    code: int
    message: str
    data: dict
