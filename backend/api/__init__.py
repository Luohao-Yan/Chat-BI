from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.endpoints import router as api_router
from api.utils.logging_utils import setup_logging

# 设置日志记录
setup_logging()

app = FastAPI()

# 配置CORS
origins = [
    "http://localhost:3000",  # 前端开发服务器地址
    "http://127.0.0.1:3000",  # 前端开发服务器地址
    # 你可以在这里添加更多允许的源地址
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 包含路由
app.include_router(api_router)