#  Copyright (c) 2017-2026 null. All rights reserved.
import os
import time

from apscheduler.schedulers.background import BackgroundScheduler

from app.core.config import UPLOAD_DIR, FILE_EXPIRY_MINUTES, CLEANUP_INTERVAL_MINUTES
from app.utils.logger import logger

scheduler = BackgroundScheduler()


def clean_expired_files():
    """清理过期文件"""
    if not os.path.exists(UPLOAD_DIR):
        return

    current_time = time.time()
    expiry_threshold = current_time - FILE_EXPIRY_MINUTES * 60

    for filename in os.listdir(UPLOAD_DIR):
        file_path = os.path.join(UPLOAD_DIR, filename)
        if os.path.isfile(file_path):
            file_mtime = os.path.getmtime(file_path)
            if file_mtime < expiry_threshold:
                try:
                    os.remove(file_path)
                    logger.info(f"已删除过期文件: {filename}")
                except Exception as e:
                    logger.error(f"删除文件 {filename} 时出错: {str(e)}")


def start_scheduler():
    """启动定时任务调度器"""
    scheduler.add_job(
        clean_expired_files,
        'interval',
        minutes=CLEANUP_INTERVAL_MINUTES,
        id='clean_expired_files',
        replace_existing=True,
    )
    scheduler.start()
    logger.info("定时任务调度器已启动")


def stop_scheduler():
    """停止定时任务调度器"""
    scheduler.shutdown()
    logger.info("定时任务调度器已停止")
