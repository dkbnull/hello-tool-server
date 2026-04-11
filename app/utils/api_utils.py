#  Copyright (c) 2017-2026 null. All rights reserved.
import os

from fastapi import UploadFile, HTTPException

from app.core.config import MAX_FILE_SIZE
from app.utils.file_utils import get_unique_filename, validate_file, get_file_path
from app.utils.logger import logger


async def process_uploaded_file(file: UploadFile, allowed_extensions: list):
    """处理上传的文件：校验、大小检查、保存"""
    if not validate_file(file, allowed_extensions):
        logger.warning(f"文件类型错误，文件名: {file.filename}")
        raise HTTPException(status_code=400, detail=f"仅支持{','.join(allowed_extensions)}格式文件")

    content = await file.read()
    file_size = len(content)
    logger.info(f"文件大小: {file_size / 1024 / 1024:.2f}MB")

    if file_size > MAX_FILE_SIZE:
        logger.warning(f"文件大小超过限制，文件名: {file.filename}，大小: {file_size / 1024 / 1024:.2f}MB")
        raise HTTPException(status_code=400, detail="文件大小超过限制，最大支持10MB")

    filename = get_unique_filename(file.filename, allowed_extensions[0])
    file_path = get_file_path(filename)
    with open(file_path, "wb") as f:
        f.write(content)
    logger.info(f"文件保存成功，文件名: {filename}")

    return filename, file_path, content


def cleanup_file(file_path: str, filename: str):
    """清理文件"""
    if os.path.exists(file_path):
        os.remove(file_path)
        logger.info(f"文件已删除: {filename}")


def create_response(filename: str, operation: str):
    """创建转换成功的响应"""
    logger.info(f"{operation}成功，输出文件名: {filename}")
    return {
        "code": 200,
        "message": "转换成功",
        "data": {
            "download_url": f"/download/{filename}",
            "filename": filename
        }
    }
