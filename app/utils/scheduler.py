#  Copyright (c) 2017-2026 null. All rights reserved.
"""定时任务调度模块，负责过期文件的定期清理"""
import os
import time

from apscheduler.schedulers.background import BackgroundScheduler

from app.core.config import settings
from app.utils.logger import logger

scheduler = BackgroundScheduler()


def clean_expired_files():
    """清理过期文件，根据 FILE_EXPIRY_MINUTES 配置判断文件是否过期"""
    if not os.path.exists(settings.UPLOAD_DIR):
        return

    current_time = time.time()
    expiry_threshold = current_time - settings.FILE_EXPIRY_MINUTES * 60

    for filename in os.listdir(settings.UPLOAD_DIR):
        file_path = os.path.join(settings.UPLOAD_DIR, filename)
        if os.path.isfile(file_path):
            file_mtime = os.path.getmtime(file_path)
            if file_mtime < expiry_threshold:
                try:
                    os.remove(file_path)
                    logger.info("已删除过期文件: %s", filename)
                except Exception as e:
                    logger.error("删除文件 %s 时出错: %s", filename, str(e), exc_info=True)


def start_scheduler():
    """启动定时任务调度器"""
    scheduler.add_job(
        clean_expired_files,
        'interval',
        minutes=settings.CLEANUP_INTERVAL_MINUTES,
        id='clean_expired_files',
        replace_existing=True,
    )
    scheduler.start()
    logger.info("定时任务调度器已启动")


def stop_scheduler():
    """停止定时任务调度器"""
    scheduler.shutdown()
    logger.info("定时任务调度器已停止")
