from fastapi import APIRouter, HTTPException
from api.schemas.user_input import UserInput
from api.utils.ai_utils import analyze_user_intent_and_generate_sql, refine_data_with_ai
from api.utils.db_utils import execute_sql_query

router = APIRouter()

@router.post("/refine_data")
async def refine_data(user_input: UserInput):
    sql_query = await analyze_user_intent_and_generate_sql(user_input.user_input)
    if sql_query:
        df = await execute_sql_query(sql_query, user_input.user_input)
        if df is not None:
            refined_data = await refine_data_with_ai(user_input.user_input, df)
            if refined_data:
                return {"refined_data": refined_data}
            else:
                raise HTTPException(status_code=500, detail="未能梳理整理数据")
        else:
            raise HTTPException(status_code=500, detail="SQL查询失败")
    else:
        raise HTTPException(status_code=500, detail="未能生成SQL语句")