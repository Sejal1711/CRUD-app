from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "mysql+pymysql://root:@localhost:3306/crud_app_db"
    JWT_SECRET: str = "your_super_secret_jwt_key_change_this_in_production"
    JWT_EXPIRES_DAYS: int = 7
    PORT: int = 8000
    ENV: str = "development"

    class Config:
        env_file = ".env"


settings = Settings()
