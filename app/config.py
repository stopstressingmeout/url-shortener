from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str
    secret_key: str
    access_token_expire_minutes: int = 30

    # Rate limiting: defaults work without any .env changes.
    rate_limit_requests: int = 60            # general: requests allowed per window
    rate_limit_window_seconds: int = 60      # the window length
    login_rate_limit_requests: int = 5       # stricter limit for POST /auth/login

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()