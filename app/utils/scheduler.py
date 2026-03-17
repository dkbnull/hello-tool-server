#  Copyright (c) 2017-2026 null. All rights reserved.
import os
import time

from apscheduler.schedulers.background import BackgroundScheduler

from app.utils.file_utils import UPLOAD_DIR

# 创建后台调度器
scheduler = BackgroundScheduler()


def clean_expired_files():
    """清理过期文件：10分钟未下载的转换文件和10分钟之前上传的PDF文件"""
    if not os.path.exists(UPLOAD_DIR):
        return

    current_time = time.time()
    ten_minutes_ago = current_time - 10 * 60  # 10分钟

    for filename in os.listdir(UPLOAD_DIR):
        file_path = os.path.join(UPLOAD_DIR, filename)
        if os.path.isfile(file_path):
            # 获取文件的修改时间
            file_mtime = os.path.getmtime(file_path)

            # 检查是否过期
            if file_mtime < ten_minutes_ago:
                try:
                    os.remove(file_path)
                    print(f"已删除过期文件: {filename}")
                except Exception as e:
                    print(f"删除文件 {filename} 时出错: {str(e)}")


def start_scheduler():
    """启动定时任务调度器"""
    # 每5分钟执行一次清理任务
    scheduler.add_job(
        clean_expired_files,
        'interval',
        minutes=5,
        id='clean_expired_files',
        replace_existing=True
    )
    scheduler.start()
    print("定时任务调度器已启动")


def stop_scheduler():
    """停止定时任务调度器"""
    scheduler.shutdown()
    print("定时任务调度器已停止")
