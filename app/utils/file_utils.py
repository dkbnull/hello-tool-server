#  Copyright (c) 2017-2026 null. All rights reserved.
import os
import uuid
from datetime import datetime

from app.core.config import UPLOAD_DIR


def get_unique_filename(original_name: str, ext: str = None) -> str:
    """
    生成唯一文件名（避免重复）
    :param original_name: 原始文件名
    :param ext: 目标后缀（如 .docx/.xlsx，可选）
    :return: 唯一文件名
    """
    if ext is None:
        ext = os.path.splitext(original_name)[1]
    unique_id = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:8]}"
    return f"{unique_id}{ext}"


def validate_file(file, allowed_extensions: list) -> bool:
    """
    校验上传文件的后缀
    :param file: 上传的文件对象
    :param allowed_extensions: 允许的后缀列表（如 ['.pdf']）
    :return: 校验结果
    """
    filename = file.filename
    if not filename:
        return False
    ext = os.path.splitext(filename)[1].lower()
    return ext in allowed_extensions


def get_file_path(filename: str) -> str:
    """
    获取文件的完整路径
    :param filename: 文件名
    :return: 完整路径
    """
    return os.path.join(UPLOAD_DIR, filename)
