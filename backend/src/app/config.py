from decouple import config


class Settings:
    DATABASE_URL: str = config("DATABASE_URL")
    JWT_SIGNING_SECRET_KEY: str = config("JWT_SIGNING_SECRET_KEY")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 300
    JWT_ALGORITHM: str = "HS256"


settings = Settings()
