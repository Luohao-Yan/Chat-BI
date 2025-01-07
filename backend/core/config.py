import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class Settings:
    API_URL_14B_CHAT: str = os.getenv("API_URL_14B_CHAT")
    API_URL_14B_GENERATE: str = os.getenv("API_URL_14B_GENERATE")
    API_URL_72B_CHAT: str = os.getenv("API_URL_72B_CHAT")
    DB_NAME: str = os.getenv("DBNAME")
    DB_USER: str = os.getenv("DBUSER")
    DB_PASSWORD: str = os.getenv("DBPGPASSWORD")
    DB_HOST: str = os.getenv("DBHOST")
    DB_PORT: str = os.getenv("DBPORT")

settings = Settings()