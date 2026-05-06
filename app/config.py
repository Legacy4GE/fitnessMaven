from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql://fmadmin:changeme@localhost/fitnessmaven"
    secret_key: str = "CHANGE-ME-IN-PRODUCTION"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    model_config = {"env_file": ".env"}


settings = Settings()
