#  Copyright (c) 2017-2026 null. All rights reserved.
import logging
import os
from logging.handlers import RotatingFileHandler

# 项目根目录
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# 日志目录
LOG_DIR = os.path.join(BASE_DIR, "logs")

# 确保日志目录存在
os.makedirs(LOG_DIR, exist_ok=True)

# 配置日志
logger = logging.getLogger("pdf_converter")
logger.setLevel(logging.INFO)

# 日志格式
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# 控制台输出
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)

# 文件输出（按大小轮转，最大10MB，保留5个备份）
file_handler = RotatingFileHandler(
    os.path.join(LOG_DIR, "pdf_converter.log"),
    maxBytes=10 * 1024 * 1024,
    backupCount=5,
    encoding='utf-8'
)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)

# 添加处理器
logger.addHandler(console_handler)
logger.addHandler(file_handler)

# 导出logger
__all__ = ["logger"]
