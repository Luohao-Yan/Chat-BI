from fastapi import APIRouter, HTTPException
from api.schemas.user_input import UserInput
from api.utils.ai_utils import analyze_user_intent_and_generate_sql
from api.utils.db_utils import execute_sql_query

router = APIRouter()

@router.post("/execute_sql")
async def execute_sql(user_input: UserInput):
    sql_query = await analyze_user_intent_and_generate_sql(user_input.user_input)
    if sql_query:
        df = await execute_sql_query(sql_query, user_input.user_input)
        if df is not None:
            return {"data": df.to_dict(orient='records')}
        else:
            raise HTTPException(status_code=500, detail="SQL查询失败")
    else:
        raise HTTPException(status_code=500, detail="未能生成SQL语句")