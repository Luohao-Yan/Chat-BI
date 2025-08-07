from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from api.schemas.user_input import UserInput
from api.utils.ai_utils import (
    analyze_user_intent_and_generate_sql,
    determine_chart_type,
    refine_data_with_ai,
    generate_insight_analysis,
)
from api.utils.db_utils import execute_sql_query
from api.dependencies.dependencies import get_async_session, redis_client
import logging
import asyncio

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/generate_chart")
async def generate_chart(
    user_input: UserInput,
    background_tasks: BackgroundTasks,
    async_session: AsyncSession = Depends(get_async_session),
):
    logger.info("Received user input for generating chart: %s", user_input)

    try:
        # 生成SQL查询语句
        sql_query = await analyze_user_intent_and_generate_sql(user_input.user_input)
        logger.info("Generated SQL query:\n %s", sql_query)
        if not sql_query:
            logger.error("Failed to generate SQL query")
            # 返回更友好的错误信息
            return {
                "error": "无法生成SQL查询语句",
                "message": "请检查您的输入是否正确，或者稍后再试",
                "data": [],
                "refined_data": "",
                "chart_type": "bar",
            }

        # 执行SQL查询
        df = await execute_sql_query(sql_query, user_input, async_session)
        logger.info("Executed SQL query, resulting DataFrame:\n %s", df)
        if df is None or df.empty:
            logger.error("SQL query execution failed or returned empty data")
            return {
                "error": "SQL查询失败或返回空数据",
                "message": "请检查数据库连接或查询语句",
                "data": [],
                "refined_data": "",
                "chart_type": "bar",
            }

        # # 生成SQL查询语句
        # sql_queries = await analyze_user_intent_and_generate_sql(user_input.user_input)
        # logger.info("Generated SQL queries:\n %s", sql_queries)
        # if not sql_queries:
        #     logger.error("Failed to generate SQL queries")
        #     raise HTTPException(status_code=500, detail="未能生成SQL语句")
        # # 执行每个SQL查询
        # data_frames = []
        # for sql_query in sql_queries:
        #     df = await execute_sql_query(sql_query, user_input, async_session)
        #     logger.info("Executed SQL query, resulting DataFrame:\n %s", df)
        #     if df is None:
        #         logger.error("SQL query execution failed")
        #         raise HTTPException(status_code=500, detail="SQL查询失败")
        #     data_frames.append(df)

        # 并发执行数据整理、图表类型判断和洞察分析
        try:
            refined_data_task = refine_data_with_ai(user_input.user_input, df)
            chart_type_task = determine_chart_type(
                user_input.user_input, df.to_json(orient="records")
            )
            # 同时开始洞察分析，但不等待完成
            insight_analysis_task = asyncio.create_task(
                generate_insight_analysis(user_input.user_input, df)
            )

            # 等待图表生成必需的数据
            refined_data, chart_type = await asyncio.gather(
                refined_data_task, chart_type_task, return_exceptions=True
            )
        except Exception as e:
            logger.error(f"AI处理失败: {e}")
            # 如果AI处理失败，使用默认值
            refined_data = "数据已准备就绪"
            chart_type = "bar"
            # 创建一个空的洞察分析任务
            insight_analysis_task = asyncio.create_task(
                asyncio.sleep(0)  # 空任务，返回None
            )

        logger.info("Refined data:\n %s", refined_data)
        logger.info("Determined chart type: %s", chart_type)

        if not refined_data:
            logger.error("Failed to refine data")
            refined_data = "数据已准备就绪"
        if not chart_type:
            logger.error("Failed to determine chart type")
            chart_type = "bar"

        # 将日期对象转换为字符串格式
        data_records = df.to_dict(orient="records")
        for record in data_records:
            for key, value in record.items():
                if isinstance(value, datetime):
                    record[key] = value.strftime("%Y-%m-%d")

        result = {
            "data": data_records,
            "refined_data": refined_data,
            "chart_type": chart_type,
        }

        # 将数据存储到Redis供流式分析使用
        await redis_client.set(
            f"chart_data:{user_input.user_input}", 
            df.to_json(orient="records"),
            ex=3600  # 1小时过期
        )

        logger.info("Successfully generated chart data:\n %s", result)

        # 将洞察分析任务添加到后台任务，但使用已经开始的任务
        background_tasks.add_task(
            store_insight_analysis, user_input.user_input, insight_analysis_task
        )

        return result
    except Exception as e:
        logger.exception("An error occurred while generating chart")
        # 返回更友好的错误信息而不是抛出异常
        return {
            "error": "生成图表时发生错误",
            "message": str(e),
            "data": [],
            "refined_data": "",
            "chart_type": "bar",
        }


async def generate_insight_analysis_task(user_input, df):
    insight_analysis = await generate_insight_analysis(user_input, df)
    if insight_analysis:
        logger.info("Generated insight analysis: %s", insight_analysis)
        # 将洞察分析结果存储到 Redis 中
        await redis_client.set(f"insight_analysis:{user_input}", insight_analysis)
    else:
        logger.error("Failed to generate insight analysis")

async def store_insight_analysis(user_input, insight_task):
    """存储已经开始的洞察分析任务结果"""
    try:
        insight_analysis = await insight_task
        if insight_analysis:
            logger.info("Generated insight analysis: %s", insight_analysis)
            # 将洞察分析结果存储到 Redis 中
            await redis_client.set(f"insight_analysis:{user_input}", insight_analysis)
        else:
            logger.error("Failed to generate insight analysis")
    except Exception as e:
        logger.error(f"Error storing insight analysis: {e}")
