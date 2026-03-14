from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "mysql+pymysql://root:@localhost:3306/crud_app_db"
    JWT_SECRET: str = "your_super_secret_jwt_key_change_this_in_production"
    JWT_EXPIRES_DAYS: int = 7
    PORT: int = 8080
    ENV: str = "development"
    FRONTEND_URL: str = "http://localhost:5173"

    class Config:
        env_file = ".env"


settings = Settings()
