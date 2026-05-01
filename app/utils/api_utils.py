#  Copyright (c) 2017-2026 null. All rights reserved.
"""API工具模块，提供文件上传处理、清理和响应创建等功能"""
import os

from fastapi import UploadFile, HTTPException

from app.core.config import settings
from app.utils.file_utils import get_unique_filename, validate_file, get_file_path
from app.utils.logger import logger


async def process_uploaded_file(file: UploadFile, allowed_extensions: list):
    """
    处理上传的文件：校验、大小检查、保存

    :param file: 上传的文件对象
    :param allowed_extensions: 允许的文件后缀列表
    :return: (文件名, 文件路径, 文件内容) 元组
    :raises HTTPException: 文件类型错误或大小超限时抛出
    """
    if not validate_file(file, allowed_extensions):
        logger.warning("文件类型错误，文件名: %s", file.filename)
        raise HTTPException(status_code=400, detail=f"仅支持{','.join(allowed_extensions)}格式文件")

    content = await file.read()
    file_size = len(content)
    logger.info("文件大小: %.2fMB", file_size / 1024 / 1024)

    if file_size > settings.MAX_FILE_SIZE:
        logger.warning("文件大小超过限制，文件名: %s，大小: %.2fMB", file.filename, file_size / 1024 / 1024)
        raise HTTPException(status_code=400, detail="文件大小超过限制，最大支持10MB")

    filename = get_unique_filename(file.filename, allowed_extensions[0])
    file_path = get_file_path(filename)
    with open(file_path, "wb") as f:
        f.write(content)
    logger.info("文件保存成功，文件名: %s", filename)

    return filename, file_path, content


def cleanup_file(file_path: str, filename: str):
    """
    清理指定文件

    :param file_path: 文件完整路径
    :param filename: 文件名（用于日志记录）
    """
    if os.path.exists(file_path):
        os.remove(file_path)
        logger.info("文件已删除: %s", filename)


def create_response(filename: str, operation: str):
    """
    创建转换成功的响应

    :param filename: 输出文件名
    :param operation: 操作名称（用于日志记录）
    :return: 标准响应字典
    """
    logger.info("%s成功，输出文件名: %s", operation, filename)
    return {
        "code": 200,
        "message": "转换成功",
        "data": {
            "download_url": f"/download/{filename}",
            "filename": filename
        }
    }
