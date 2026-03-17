#  Copyright (c) 2017-2026 null. All rights reserved.
from fastapi import FastAPI

from app.api.convert import router as convert_router
from app.utils.scheduler import start_scheduler, stop_scheduler

# 创建FastAPI应用
app = FastAPI(
    title="Hello Tool Server",
    description="提供 Hello Tool 的RESTful接口",
    version="1.0.0"
)

# 注册路由
app.include_router(convert_router)


# 应用启动事件
@app.on_event("startup")
async def startup_event():
    """应用启动时执行"""
    start_scheduler()


# 应用关闭事件
@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时执行"""
    stop_scheduler()


# 根路径测试
@app.get("/", summary="健康检查")
async def root():
    return {"code": 200, "message": "服务运行中", "version": "1.0.0"}


# 启动命令：uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",  # 允许外部访问
        port=8000,  # 端口
        reload=True  # 开发模式自动重载
    )
