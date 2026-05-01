#  Copyright (c) 2017-2026 null. All rights reserved.
"""应用配置管理模块，使用 pydantic-settings 统一管理配置项"""
import os

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用全局配置，敏感信息通过环境变量或 .env 文件注入"""

    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    UPLOAD_DIR: str = ""
    LOG_DIR: str = ""

    MAX_FILE_SIZE: int = 10 * 1024 * 1024
    FILE_EXPIRY_MINUTES: int = 10
    CLEANUP_INTERVAL_MINUTES: int = 5

    ALLOWED_IPS: str = ""
    BLOCKED_IPS: str = ""
    RATE_LIMIT_PER_IP: int = 5
    RATE_LIMIT_WINDOW: int = 1
    CSRF_TOKEN_EXPIRY: int = 3600
    SECURE_COOKIE: bool = True

    CORS_ORIGINS: str = "*"
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: str = "*"
    CORS_ALLOW_HEADERS: str = "*"

    model_config = {
        "case_sensitive": True,
        "env_file": ".env",
        "env_file_encoding": "utf-8",
    }

    def model_post_init(self, __context):
        if not self.UPLOAD_DIR:
            self.UPLOAD_DIR = os.path.join(self.BASE_DIR, "uploads")
        if not self.LOG_DIR:
            self.LOG_DIR = os.path.join(self.BASE_DIR, "logs")
        os.makedirs(self.UPLOAD_DIR, exist_ok=True)
        os.makedirs(self.LOG_DIR, exist_ok=True)

    @property
    def allowed_ips_list(self) -> list[str]:
        return [ip.strip() for ip in self.ALLOWED_IPS.split(",") if ip.strip()]

    @property
    def blocked_ips_list(self) -> list[str]:
        return [ip.strip() for ip in self.BLOCKED_IPS.split(",") if ip.strip()]

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    @property
    def cors_methods_list(self) -> list[str]:
        return [method.strip() for method in self.CORS_ALLOW_METHODS.split(",") if method.strip()]

    @property
    def cors_headers_list(self) -> list[str]:
        return [header.strip() for header in self.CORS_ALLOW_HEADERS.split(",") if header.strip()]


settings = Settings()
