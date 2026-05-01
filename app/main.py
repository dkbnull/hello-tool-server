#  Copyright (c) 2017-2026 null. All rights reserved.
"""应用入口模块，初始化FastAPI应用并配置中间件、路由和异常处理"""
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.api.auth import router as auth_router
from app.api.convert import router as convert_router
from app.core.config import settings
from app.core.exceptions import AppException
from app.utils.limiter import limiter
from app.utils.logger import logger
from app.utils.scheduler import start_scheduler, stop_scheduler
from app.utils.security import SecurityMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理，启动和停止定时任务调度器"""
    start_scheduler()
    yield
    stop_scheduler()


app = FastAPI(
    title="Hello Tool Server",
    description="提供 Hello Tool 的RESTful接口",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    SecurityMiddleware,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.cors_methods_list,
    allow_headers=settings.cors_headers_list,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    """
    全局自定义异常处理器，将AppException转换为结构化JSON响应

    :param request: 请求对象
    :param exc: 捕获的应用异常
    :return: 结构化错误响应
    """
    logger.error("请求异常，路径: %s，异常: %s", request.url.path, exc.message, exc_info=True)
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "code": exc.code,
            "message": exc.message,
        }
    )


app.include_router(auth_router)
app.include_router(convert_router)


@app.get("/", summary="健康检查", description="检查服务是否正常运行")
async def root():
    return {"code": 200, "message": "服务运行中", "version": "1.0.0"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
