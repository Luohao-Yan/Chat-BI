import os
from fastapi import FastAPI
from api.endpoints import create_tables, insert_data, generate_sql, execute_sql, refine_data, determine_chart
from api.utils.logging_utils import setup_logging
import uvicorn

app = FastAPI()

# 包含路由
app.include_router(create_tables.router, prefix="/api")
app.include_router(insert_data.router, prefix="/api")
app.include_router(generate_sql.router, prefix="/api")
app.include_router(execute_sql.router, prefix="/api")
app.include_router(refine_data.router, prefix="/api")
app.include_router(determine_chart.router, prefix="/api")

if __name__ == "__main__":
    host = os.getenv("FASTAPI_HOST", "0.0.0.0")  # 默认值为 "0.0.0.0"
    environment = os.getenv("FASTAPI_ENV", "production")  # 默认值为 "production"
    reload = environment == "development"
    uvicorn.run(app='main:app', host=host, port=9100, reload=reload)