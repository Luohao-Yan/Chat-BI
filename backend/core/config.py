import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class Settings:
    API_URL_14B_CHAT: str = os.getenv("API_URL_14B_CHAT", "http://localhost:11434/api/chat")
    API_URL_14B_GENERATE: str = os.getenv("API_URL_14B_GENERATE", "http://localhost:11434/api/generate")
    API_URL_72B_CHAT: str = os.getenv("API_URL_72B_CHAT", "http://10.255.4.2:8005/v1/chat/completions")
    
    DB_NAME: str = os.getenv("DBNAME", "chabi_template")
    DB_USER: str = os.getenv("DBUSER", "aigcgen")
    DB_PASSWORD: str = os.getenv("DBPGPASSWORD", "Louis!123456")
    DB_HOST: str = os.getenv("DBHOST", "127.0.0.1")
    DB_PORT: str = os.getenv("DBPORT", "5433")
    
    FASTAPI_HOST: str = os.getenv("FASTAPI_HOST", "127.0.0.1")
    FASTAPI_PORT: int = int(os.getenv("FASTAPI_PORT", 11434))
    FASTAPI_ENV: str = os.getenv("FASTAPI_ENV", "development")
    RELOAD: bool = FASTAPI_ENV == "development"
    FASTAPI_WORKERS: int = int(os.getenv("FASTAPI_WORKERS", 1))
    FASTAPI_LOG_LEVEL: str = os.getenv("FASTAPI_LOG_LEVEL", "debug")
    FASTAPI_RELOAD: bool = os.getenv("FASTAPI_RELOAD", "True").lower() in ("true", "1", "t")
    FASTAPI_DEBUG: bool = os.getenv("FASTAPI_DEBUG", "True").lower() in ("true", "1", "t")
    FASTAPI_SECRET: str = os.getenv("FASTAPI_SECRET", "")
    
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:3000")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "Louis!123456")
    TOKEN_EXPIRE_MINUTES: int = int(os.getenv("TOKEN_EXPIRE_MINUTES", 30))

    # 组合生成 DATABASE_URL
    DATABASE_URL: str = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

    @property
    def RELOAD(self) -> bool:
        return self.FASTAPI_ENV == "development"

settings = Settings()