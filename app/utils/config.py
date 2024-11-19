from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str
    echo_sql: bool = False

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
