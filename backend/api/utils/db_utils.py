import logging
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from db.session import async_session
import pandas as pd
from core.config import settings
from api.schemas.user_input import UserInput
from api.utils.ai_utils import analyze_user_intent_and_generate_sql  # 导入函数
from sqlalchemy.sql import text

# 加载环境变量
load_dotenv()

# 从配置中获取数据库连接信息
DBNAME = settings.DB_NAME
DBUSER = settings.DB_USER
DBPGPASSWORD = settings.DB_PASSWORD
DBHOST = settings.DB_HOST
DBPORT = settings.DB_PORT

async def execute_sql_query(sql_query: str, user_input, async_session: AsyncSession, retry_count=3):
    async with async_session as session:  # 修改这里
        async with session.begin():
            for attempt in range(retry_count):
                try:
                    result = await session.execute(text(sql_query))
                    df = pd.DataFrame(result.fetchall(), columns=result.keys())
                    return df
                except Exception as e:
                    logging.error(f"SQL查询错误: {e}")
                    if attempt < retry_count - 1:
                        logging.info("重新生成SQL查询语句并重试...")
                        sql_query = await analyze_user_intent_and_generate_sql(user_input.user_input)
                        if not sql_query:
                            logging.error("重新生成SQL查询语句失败")
                            return None
                    else:
                        logging.error("多次尝试后仍未能成功执行SQL查询")
                        return None