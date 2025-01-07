from fastapi import APIRouter, HTTPException
from api.schemas.user_input import FilePathInput
from api.utils.db_utils import insert_data_from_file

router = APIRouter()

@router.post("/insert_data")
async def insert_data_endpoint(file_path: FilePathInput):
    try:
        await insert_data_from_file(file_path.file_path)
        return {"message": "数据插入成功"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"插入数据时出错: {e}")