import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.config import settings
import uvicorn
import logging
from api.endpoints import router as api_router
from contextlib import asynccontextmanager
from api.dependencies.dependencies import redis_client, engine
from core.logging import setup_logging
from db.init_db import init_db, insert_mock_data  # 导入数据库初始化和插入mock数据函数

# 设置日志记录
setup_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 在应用启动时执行的代码
    await init_db()  # 调用数据库初始化函数
    await insert_mock_data()  # 插入mock数据
    yield
    # 在应用关闭时执行的代码
    await redis_client.close()
    await engine.dispose()

# 创建 FastAPI 实例并传入 lifespan 事件处理程序
app = FastAPI(lifespan=lifespan)

# 配置CORS
origins = [
    settings.FRONTEND_URL,
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

if __name__ == "__main__":
    uvicorn.run(app='main:app', host=settings.FASTAPI_HOST, port=settings.FASTAPI_PORT, reload=settings.RELOAD)