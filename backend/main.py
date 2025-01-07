import os
from fastapi import FastAPI
from api.endpoints import router as api_router
import uvicorn

app = FastAPI()

app.include_router(api_router)

if __name__ == "__main__":
    host = os.getenv("FASTAPI_HOST", "0.0.0.0")  # 默认值为 "0.0.0.0"
    environment = os.getenv("FASTAPI_ENV", "production")  # 默认值为 "production"
    reload = environment == "development"
    uvicorn.run(app='main:app', host=host, port=9100, reload=reload)