import os
from typing import Optional
from pydantic.dataclasses import dataclass


@dataclass
class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    ALEMBIC_DATABASE_URL: Optional[str] = os.getenv("ALEMBIC_DATABASE_URL")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "")
    ALGORITHM: str = os.getenv("ALGORITHM", "")
    ECHO_SQL: bool = os.getenv("ECHO_SQL", "false").lower() == "true"
    API_KEYS: str = os.getenv("API_KEYS", "")
    WANT_SINGLE_SIGNIN: bool = os.getenv("WANT_SINGLE_SIGNIN", "false").lower() == "true"
    BASE_URL: str = os.getenv("BASE_URL", "")
    COOKIE_DOMAIN: str = os.getenv("COOKIE_DOMAIN", "")
    REDIS_URL: str = os.getenv("REDIS_URL", "")


@dataclass
class EmailSettings:
    MAIL_USERNAME: str = os.getenv("MAIL_USERNAME", "")
    MAIL_PASSWORD: str = os.getenv("MAIL_PASSWORD", "")
    MAIL_FROM: str = os.getenv("MAIL_FROM", "email@example.com")
    MAIL_PORT: int = int(os.getenv("MAIL_PORT", "587"))
    MAIL_SERVER: str = os.getenv("MAIL_SERVER", "")
    MAIL_STARTTLS: bool = os.getenv("MAIL_STARTTLS", "true").lower() == "true"
    MAIL_SSL_TLS: bool = os.getenv("MAIL_SSL_TLS", "false").lower() == "true"
    USE_CREDENTIALS: bool = os.getenv("USE_CREDENTIALS", "true").lower() == "true"
    VALIDATE_CERTS: bool = os.getenv("VALIDATE_CERTS", "true").lower() == "true"


def get_email_settings():
    return EmailSettings()


def get_app_settings():
    return Settings()
