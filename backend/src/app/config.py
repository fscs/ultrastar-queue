from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )
    DATABASE_URL: str
    JWT_SIGNING_SECRET_KEY: str
    PATH_TO_ULTRASTAR_SONG_DIR: str
    ADMIN_USERNAME: str
    ADMIN_PASSWORD: str

    FRONTEND_HOST: str = "localhost"
    FRONTEND_PORT: int = 5173
    BACKEND_HOST: str = "localhost"
    BACKEND_PORT: int = 8000

    SWAGGER_UI_URL: str | None = None
    REDOC_URL: str | None = None

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 300
    JWT_ALGORITHM: str = "HS256"


settings = Settings()
