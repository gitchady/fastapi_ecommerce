import os
from dotenv import load_dotenv


load_dotenv()


def _parse_bool_env(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _parse_csv_env(name: str) -> tuple[str, ...]:
    raw_value = os.getenv(name, "")
    return tuple(item.strip() for item in raw_value.split(",") if item.strip())

YOOKASSA_SHOP_ID = os.getenv("YOOKASSA_SHOP_ID")
YOOKASSA_SECRET_KEY = os.getenv("YOOKASSA_SECRET_KEY")
YOOKASSA_RETURN_URL = os.getenv("YOOKASSA_RETURN_URL", "http://localhost:8000/")

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY is not set. Add it to .env")

ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ASYNC_DATABASE_URL = os.getenv("ASYNC_DATABASE_URL")
if not ASYNC_DATABASE_URL:
    raise RuntimeError("ASYNC_DATABASE_URL is not set. Add PostgreSQL DSN to .env")
if not ASYNC_DATABASE_URL.startswith("postgresql+asyncpg://"):
    raise RuntimeError("ASYNC_DATABASE_URL must start with 'postgresql+asyncpg://'")

AUTO_CREATE_TABLES = _parse_bool_env("AUTO_CREATE_TABLES", default=False)
TRUSTED_PROXY_IPS = _parse_csv_env("TRUSTED_PROXY_IPS")
