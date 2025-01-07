from fastapi import APIRouter, HTTPException
from api.schemas.user_input import UserInput
from api.utils.ai_utils import analyze_user_intent_and_generate_sql, determine_chart_type
from api.utils.db_utils import execute_sql_query

router = APIRouter()

@router.post("/determine_chart")
async def determine_chart(user_input: UserInput):
    sql_query = await analyze_user_intent_and_generate_sql(user_input.user_input)
    if sql_query:
        df = await execute_sql_query(sql_query, user_input.user_input)
        if df is not None:
            chart_type = await determine_chart_type(user_input.user_input, df.to_json(orient='records'))
            if chart_type:
                return {"chart_type": chart_type}
            else:
                raise HTTPException(status_code=500, detail="未能确定图表类型")
        else:
            raise HTTPException(status_code=500, detail="SQL查询失败")
    else:
        raise HTTPException(status_code=500, detail="未能生成SQL语句")