from fastapi import APIRouter, HTTPException
from api.utils.db_utils import create_tables

router = APIRouter()

@router.post("/create_tables")
async def create_tables_endpoint():
    try:
        await create_tables()
        return {"message": "表创建成功"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建表时出错: {e}")