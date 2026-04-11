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
from app.utils.security import SecurityMiddleware, SECURITY_CONFIG

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
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
    allowed_ips=SECURITY_CONFIG["allowed_ips"],
    blocked_ips=SECURITY_CONFIG["blocked_ips"],
    rate_limit_per_ip=SECURITY_CONFIG["rate_limit_per_ip"],
    rate_limit_window=SECURITY_CONFIG["rate_limit_window"],
    csrf_token_expiry=SECURITY_CONFIG["csrf_token_expiry"],
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.include_router(convert_router)
app.include_router(auth_router)


@app.get("/", summary="健康检查")
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
