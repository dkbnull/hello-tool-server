#  Copyright (c) 2017-2026 null. All rights reserved.
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.api.auth import router as auth_router
from app.api.convert import router as convert_router
from app.utils.limiter import limiter
from app.utils.scheduler import start_scheduler, stop_scheduler

# 加载.env文件
load_dotenv()


# 创建FastAPI应用
@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    start_scheduler()
    yield
    # 关闭时执行
    stop_scheduler()


app = FastAPI(
    title="Hello Tool Server",
    description="提供 Hello Tool 的RESTful接口",
    version="1.0.0",
    lifespan=lifespan
)

# 添加安全中间件
from app.utils.security import SecurityMiddleware, SECURITY_CONFIG

app.add_middleware(
    SecurityMiddleware,
    allowed_ips=SECURITY_CONFIG["allowed_ips"],
    blocked_ips=SECURITY_CONFIG["blocked_ips"],
    rate_limit_per_ip=SECURITY_CONFIG["rate_limit_per_ip"],
    rate_limit_window=SECURITY_CONFIG["rate_limit_window"],
    csrf_token_expiry=SECURITY_CONFIG["csrf_token_expiry"]
)

# 添加限流异常处理
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# 注册路由
app.include_router(convert_router)
app.include_router(auth_router)


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
