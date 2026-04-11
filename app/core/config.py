#  Copyright (c) 2017-2026 null. All rights reserved.
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
LOG_DIR = os.path.join(BASE_DIR, "logs")

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

MAX_FILE_SIZE = int(os.environ.get("MAX_FILE_SIZE", str(10 * 1024 * 1024)))

FILE_EXPIRY_MINUTES = int(os.environ.get("FILE_EXPIRY_MINUTES", "10"))
CLEANUP_INTERVAL_MINUTES = int(os.environ.get("CLEANUP_INTERVAL_MINUTES", "5"))

SECURITY_CONFIG = {
    "allowed_ips": [ip.strip() for ip in os.environ.get("ALLOWED_IPS", "").split(",") if ip.strip()],
    "blocked_ips": [ip.strip() for ip in os.environ.get("BLOCKED_IPS", "").split(",") if ip.strip()],
    "rate_limit_per_ip": int(os.environ.get("RATE_LIMIT_PER_IP", "5")),
    "rate_limit_window": int(os.environ.get("RATE_LIMIT_WINDOW", "1")),
    "csrf_token_expiry": int(os.environ.get("CSRF_TOKEN_EXPIRY", "3600")),
}
