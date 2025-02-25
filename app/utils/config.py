from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import EmailStr

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str
    echo_sql: bool = False
    API_KEYS: str
    WANT_SINGLE_SIGNIN: bool

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

class EmailSettings(BaseSettings):
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: EmailStr
    MAIL_PORT: int
    MAIL_SERVER: str
    MAIL_STARTTLS: bool
    MAIL_SSL_TLS: bool
    USE_CREDENTIALS: bool
    VALIDATE_CERTS: bool


    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


email_settings = EmailSettings()
settings = Settings()
