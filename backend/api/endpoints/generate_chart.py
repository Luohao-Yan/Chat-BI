from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from api.schemas.user_input import UserInput
from api.utils.ai_utils import analyze_user_intent_and_generate_sql, determine_chart_type, refine_data_with_ai
from api.utils.db_utils import execute_sql_query
from api.dependencies.dependencies import get_async_session
import logging
import asyncio

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/generate_chart")
async def generate_chart(user_input: UserInput, async_session: AsyncSession = Depends(get_async_session)):
    logger.info("Received user input for generating chart: %s", user_input)

    try:
        # 生成SQL查询语句
        sql_query = await analyze_user_intent_and_generate_sql(user_input.user_input)
        logger.info("Generated SQL query:\n %s", sql_query)
        if not sql_query:
            logger.error("Failed to generate SQL query")
            raise HTTPException(status_code=500, detail="未能生成SQL语句")

        # 执行SQL查询
        df = await execute_sql_query(sql_query, user_input, async_session)
        logger.info("Executed SQL query, resulting DataFrame:\n %s", df)
        if df is None:
            logger.error("SQL query execution failed")
            raise HTTPException(status_code=500, detail="SQL查询失败")

        # 并发执行数据整理和图表类型判断
        refined_data_task = refine_data_with_ai(user_input.user_input, df)
        chart_type_task = determine_chart_type(user_input.user_input, df.to_json(orient='records'))

        refined_data, chart_type = await asyncio.gather(refined_data_task, chart_type_task)

        logger.info("Refined data:\n %s", refined_data)
        logger.info("Determined chart type: %s", chart_type)

        if not refined_data:
            logger.error("Failed to refine data")
            raise HTTPException(status_code=500, detail="未能梳理整理数据")
        if not chart_type:
            logger.error("Failed to determine chart type")
            raise HTTPException(status_code=500, detail="未能确定图表类型")

        # 将日期对象转换为字符串格式
        data_records = df.to_dict(orient='records')
        for record in data_records:
            for key, value in record.items():
                if isinstance(value, datetime):
                    record[key] = value.strftime('%Y-%m-%d')

        result = {
            "data": data_records,
            "refined_data": refined_data,
            "chart_type": chart_type
        }

        logger.info("Successfully generated chart data:\n %s", result)
        return result
    except Exception as e:
        logger.exception("An error occurred while generating chart")
        raise HTTPException(status_code=500, detail=str(e))