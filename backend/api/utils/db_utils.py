import logging
import psycopg2
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

# 启用 PostGIS 扩展的 SQL 语句
enable_postgis_sql = """
CREATE EXTENSION IF NOT EXISTS postgis;
"""

# 创建表的 SQL 语句
create_tables_sql = """
CREATE TABLE IF NOT EXISTS pl_mobile_people_flow_data (
    id SERIAL PRIMARY KEY,
    all_count INT,
    in_count INT,
    out_count INT,
    statistics_date DATE,
    activation FLOAT DEFAULT 0,
    base_line_value FLOAT DEFAULT 0
)
WITH (fillfactor=80);

COMMENT ON COLUMN pl_mobile_people_flow_data.all_count IS '高新区日人流量';
COMMENT ON COLUMN pl_mobile_people_flow_data.in_count IS '进高新区';
COMMENT ON COLUMN pl_mobile_people_flow_data.out_count IS '出高新区';
COMMENT ON COLUMN pl_mobile_people_flow_data.statistics_date IS '统计日期';
COMMENT ON COLUMN pl_mobile_people_flow_data.activation IS '活跃度';
COMMENT ON COLUMN pl_mobile_people_flow_data.base_line_value IS '活跃度基线值';
COMMENT ON TABLE pl_mobile_people_flow_data IS '生产生活-运营商人流监测';

CREATE TABLE IF NOT EXISTS mobile_day_flow_tag (
    id SERIAL PRIMARY KEY,
    area VARCHAR(50),
    label_cnt INT,
    tag VARCHAR(50),
    label VARCHAR(50),
    type SMALLINT,
    day VARCHAR(10),
    create_time TIMESTAMP DEFAULT now()
)
WITH (fillfactor=80);

COMMENT ON COLUMN mobile_day_flow_tag.label_cnt IS '人数';
COMMENT ON COLUMN mobile_day_flow_tag.tag IS '标签类别，例如省外来源，省内来源，性别，年龄等';
COMMENT ON COLUMN mobile_day_flow_tag.label IS '标签名称，例如标签类别为省内来源时，标签名称为“珠海”';
COMMENT ON COLUMN mobile_day_flow_tag.type IS '1=日驻留、2=新流入、3=新流出';

CREATE TABLE IF NOT EXISTS pl_pop_trend_of_end_year (
    date_time VARCHAR(10) PRIMARY KEY,
    num FLOAT,
    create_time TIMESTAMP DEFAULT now()
)
WITH (fillfactor=80);

COMMENT ON COLUMN pl_pop_trend_of_end_year.num IS '单位(万)';
COMMENT ON TABLE pl_pop_trend_of_end_year IS '年末常驻人口变化趋势';

CREATE TABLE IF NOT EXISTS grid_first_level_info (
    community VARCHAR(30) PRIMARY KEY,
    grid_leader VARCHAR(1000),
    build_num INT DEFAULT 0,
    population INT DEFAULT 0,
    inconvenience_num INT DEFAULT 0,
    disable_num INT DEFAULT 0,
    other_pop_num INT DEFAULT 0,
    geom GEOMETRY,
    overview VARCHAR(500),
    area FLOAT,
    resident_population INT,
    registered_population INT,
    total_population INT,
    location VARCHAR(50),
    mac VARCHAR(255)
)
WITH (fillfactor=80);

COMMENT ON COLUMN grid_first_level_info.community IS '社区';
COMMENT ON COLUMN grid_first_level_info.grid_leader IS '网格长信息';
COMMENT ON COLUMN grid_first_level_info.build_num IS '楼栋数';
COMMENT ON COLUMN grid_first_level_info.population IS '人数';
COMMENT ON COLUMN grid_first_level_info.inconvenience_num IS '行动不便人数';
COMMENT ON COLUMN grid_first_level_info.disable_num IS '残疾人人数';
COMMENT ON COLUMN grid_first_level_info.other_pop_num IS '港澳台外籍人数';
COMMENT ON COLUMN grid_first_level_info.geom IS '地理信息';
COMMENT ON COLUMN grid_first_level_info.overview IS '概况';
COMMENT ON COLUMN grid_first_level_info.area IS '社区面积（平方公里）';
COMMENT ON COLUMN grid_first_level_info.resident_population IS '常住人口';
COMMENT ON COLUMN grid_first_level_info.registered_population IS '户籍人口';
COMMENT ON COLUMN grid_first_level_info.total_population IS '总居住人口';
COMMENT ON COLUMN grid_first_level_info.location IS '中心坐标';
COMMENT ON COLUMN grid_first_level_info.mac IS 'grid_leader字段的mac值';
COMMENT ON TABLE grid_first_level_info IS '一级社区网格信息';
"""

async def create_tables():
    conn = None
    try:
        # 连接到 PostgreSQL 数据库
        conn = psycopg2.connect(
            dbname=DBNAME,
            user=DBUSER,
            password=DBPGPASSWORD,
            host=DBHOST,
            port=DBPORT
        )
        cur = conn.cursor()
        
        # 启用 PostGIS 扩展
        logging.info("正在启用 PostGIS 扩展...")
        cur.execute(enable_postgis_sql)
        conn.commit()
        logging.info("PostGIS 扩展启用成功")

        # 创建表
        logging.info("正在创建表...")
        cur.execute(create_tables_sql)
        conn.commit()
        logging.info("表创建成功")

        # 关闭游标和连接
        cur.close()
    except Exception as e:
        logging.error(f"数据库操作错误: {e}")
    finally:
        if conn:
            conn.close()

async def insert_data_from_file(file_path):
    conn = None
    try:
        # 连接到PostgreSQL数据库
        conn = psycopg2.connect(
            dbname=DBNAME,
            user=DBUSER,
            password=DBPGPASSWORD,
            host=DBHOST,
            port=DBPORT
        )
        cur = conn.cursor()
        
        # 读取SQL文件内容
        with open(file_path, 'r', encoding='utf-8') as file:
            sql_content = file.read()
        
        # 执行SQL文件中的插入语句
        logging.info("正在插入数据...")
        cur.execute(sql_content)
        conn.commit()
        logging.info("数据插入成功")

        # 关闭游标和连接
        cur.close()
    except Exception as e:
        logging.error(f"数据库操作错误: {e}")
    finally:
        if conn:
            conn.close()

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