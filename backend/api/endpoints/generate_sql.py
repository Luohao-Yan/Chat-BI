from fastapi import APIRouter, HTTPException
from api.schemas.user_input import UserInput
from api.utils.ai_utils import analyze_user_intent_and_generate_sql

router = APIRouter()

@router.post("/generate_sql")
async def generate_sql(user_input: UserInput):
    sql_query = await analyze_user_intent_and_generate_sql(user_input.user_input)
    if sql_query:
        return {"sql_query": sql_query}
    else:
        raise HTTPException(status_code=500, detail="未能生成SQL语句")