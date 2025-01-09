from fastapi import APIRouter
from . import create_tables, insert_data, generate_chart

router = APIRouter()

router.include_router(create_tables.router, prefix="/api", tags=["create_tables"])
router.include_router(insert_data.router, prefix="/api", tags=["insert_data"])
router.include_router(generate_chart.router, prefix="/api", tags=["generate_chart"])