from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from api.schemas import UserInput
from api.utils import analyze_user_intent_and_generate_sql, execute_sql_query, refine_data_with_ai, determine_chart_type

router = APIRouter()

@router.post("/generate_sql")
async def generate_sql(user_input: UserInput):
    sql_query = await analyze_user_intent_and_generate_sql(user_input.user_input)
    if sql_query:
        return JSONResponse(content={"sql_query": sql_query})
    else:
        raise HTTPException(status_code=500, detail="未能生成SQL语句")

@router.post("/execute_sql")
async def execute_sql(user_input: UserInput):
    sql_query = await analyze_user_intent_and_generate_sql(user_input.user_input)
    if sql_query:
        df = await execute_sql_query(sql_query)
        if df is not None:
            return JSONResponse(content={"data": df.to_dict(orient='records')})
        else:
            raise HTTPException(status_code=500, detail="SQL查询失败")
    else:
        raise HTTPException(status_code=500, detail="未能生成SQL语句")

@router.post("/refine_data")
async def refine_data(user_input: UserInput):
    sql_query = await analyze_user_intent_and_generate_sql(user_input.user_input)
    if sql_query:
        df = await execute_sql_query(sql_query)
        if df is not None:
            refined_data = await refine_data_with_ai(user_input.user_input, df)
            if refined_data:
                return JSONResponse(content={"refined_data": refined_data})
            else:
                raise HTTPException(status_code=500, detail="未能梳理整理数据")
        else:
            raise HTTPException(status_code=500, detail="SQL查询失败")
    else:
        raise HTTPException(status_code=500, detail="未能生成SQL语句")

@router.post("/determine_chart")
async def determine_chart(user_input: UserInput):
    sql_query = await analyze_user_intent_and_generate_sql(user_input.user_input)
    if sql_query:
        df = await execute_sql_query(sql_query)
        if df is not None:
            chart_type = await determine_chart_type(user_input.user_input, json.dumps(df.to_dict(orient='records')))
            if chart_type:
                return JSONResponse(content={"chart_type": chart_type})
            else:
                raise HTTPException(status_code=500, detail="未能确定图表类型")
        else:
            raise HTTPException(status_code=500, detail="SQL查询失败")
    else:
        raise HTTPException(status_code=500, detail="未能生成SQL语句")