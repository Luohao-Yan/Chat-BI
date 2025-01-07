import os
import time
import requests
import json
import logging
import psycopg2
import pandas as pd
import plotly.express as px
import plotly.utils
import kaleido
import plotly.io as pio
from io import StringIO
from psycopg2 import sql
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

# 配置日志记录
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# 初始化session对象并配置重试机制
session = requests.Session()
retries = Retry(total=5, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
session.mount('http://', HTTPAdapter(max_retries=retries))
session.mount('https://', HTTPAdapter(max_retries=retries))

# 使用模型选择
# 定义模型类型变量
model_type = "72B-chat"  # 可以是 "14B-chat", "14B-generate", "72B-chat"

# 定义模型配置映射
model_config = {
    "14B-chat": {
        "api_url": "http://localhost:11434/api/chat",
        "model": "qwen2.5:14b",
        "call_function": "call_qwen_chat_14B_api",
    },
    "14B-generate": {
        "api_url": "http://localhost:11434/api/generate",
        "model": "qwen2.5:14b",
        "call_function": "call_qwen_generate_14B_api",
    },
    "72B-chat": {
        "api_url": "http://10.255.4.2:8005/v1/chat/completions",
        "model": "/root/.cache/modelscope",
        "call_function": "call_qwen_chat_72B_api",
    },
}

def make_api_request(api_url, headers, data):
    """
    通用的API请求函数，处理请求和错误。

    :param api_url: API的URL
    :param headers: 请求头
    :param data: 请求数据
    :return: API响应的JSON数据或None
    """
    try:
        response = session.post(api_url, headers=headers, data=json.dumps(data), timeout=120)
        response.raise_for_status()
        if response.text.strip():
            return response.json()
        else:
            logging.error("API响应为空")
            return None
    except requests.exceptions.RequestException as e:
        logging.error(f"HTTP请求错误: {e}")
        return None
    except json.JSONDecodeError as e:
        logging.error(f"JSON解析错误: {e}")
        return None

# 千问2.5 模型调用
def call_qwen_chat_14B_api(api_url, model, system_prompt, user_input):
    headers = {"Content-Type": "application/json"}
    data = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input},
        ],
        "temperature": 0.5,
        "top_p": 1,
        "repetition_penalty": 1.05,
        "max_tokens": 4000,
        "stream": False,
    }
    result = make_api_request(api_url, headers, data)
    if result and "message" in result and "content" in result["message"]:
        return result["message"]["content"]
    else:
        logging.error("API响应中没有预期的'message'或'content'字段")
        return None

def call_qwen_generate_14B_api(api_url, model, system_prompt):
    headers = {"Content-Type": "application/json"}
    data = {
        "model": model,
        "prompt": system_prompt,
        "stream": False,
    }
    result = make_api_request(api_url, headers, data)
    if result and "response" in result:
        return result["response"]
    else:
        logging.error("API响应中没有预期的'response'字段")
        return None

def call_qwen_chat_72B_api(api_url, model, system_prompt, user_input=None):
    headers = {"Content-Type": "application/json"}
    messages = [{"role": "system", "content": system_prompt}]
    if user_input:
        messages.append({"role": "user", "content": user_input})

    data = {
        "model": model,
        "messages": messages,
        "temperature": 0.7,
        "top_p": 0.8,
        "repetition_penalty": 1.05,
        "stream": False,
    }
    result = make_api_request(api_url, headers, data)
    if result and "choices" in result and len(result["choices"]) > 0:
        message = result["choices"][0]["message"]
        if "content" in message:
            return message["content"]
        else:
            logging.error("API响应中没有预期的'content'字段")
            return None
    else:
        logging.error("API响应中没有预期的'choices'字段或'choices'为空")
        return None

# 统一请求qwen2.5 模型调用函数
def call_qwen_model(model_type, system_prompt, user_input=None):
    config = model_config.get(model_type)
    if not config:
        logging.error("未知的模型类型")
        return None

    api_url = config["api_url"]
    model = config["model"]
    call_function = config["call_function"]

    if call_function == "call_qwen_chat_14B_api":
        return call_qwen_chat_14B_api(api_url, model, system_prompt, user_input)
    elif call_function == "call_qwen_generate_14B_api":
        return call_qwen_generate_14B_api(api_url, model, system_prompt)
    elif call_function == "call_qwen_chat_72B_api":
        return call_qwen_chat_72B_api(api_url, model, system_prompt, user_input)
    else:
        logging.error("未知的调用函数")
        return None

def analyze_user_intent_and_generate_sql(user_input, retry_count=3):
    """
    分析用户的输入意图并生成相应的SQL语句。

    :param user_input: 用户的输入
    :param retry_count: 重试次数
    :return: 生成的SQL语句或None
    """
    # 定义系统提示，要求生成的SQL语句必须是Markdown格式
    system_prompt = (
        "Analyze the user input and generate the corresponding SQL query based on the existing database table clause. "
        """My database build statement:\n\n
        珠海高新区人口概览信息流水表:CREATE TABLE "public"."pl_mobile_people_flow_data" (
  "id" int4 NOT NULL DEFAULT nextval('mobile_people_id_seq'::regclass),
  "all_count" int4,
  "in_count" int4,
  "out_count" int4,
  "statistics_date" date,
  "activation" float4 DEFAULT 0,
  "base_line_value" float4 DEFAULT 0,
  CONSTRAINT "pl_mobile_people_flow_data_pkey" PRIMARY KEY ("id")
)
WITH (fillfactor=80)
;

ALTER TABLE "public"."pl_mobile_people_flow_data" 
  OWNER TO "postgres";

COMMENT ON COLUMN "public"."pl_mobile_people_flow_data"."all_count" IS '高新区日人流量';

COMMENT ON COLUMN "public"."pl_mobile_people_flow_data"."in_count" IS '进高新区';

COMMENT ON COLUMN "public"."pl_mobile_people_flow_data"."out_count" IS '出高新区';

COMMENT ON COLUMN "public"."pl_mobile_people_flow_data"."statistics_date" IS '统计日期';

COMMENT ON COLUMN "public"."pl_mobile_people_flow_data"."activation" IS '活跃度';

COMMENT ON COLUMN "public"."pl_mobile_people_flow_data"."base_line_value" IS '活跃度基线值';

COMMENT ON TABLE "public"."pl_mobile_people_flow_data" IS '生产生活-运营商人流监测';
珠海市高新区人口流动城市明细表:
CREATE TABLE "public"."mobile_day_flow_tag" (
  "id" int4 NOT NULL DEFAULT nextval('mobile_day_flow_tag_id_seq'::regclass),
  "area" varchar(50) COLLATE "pg_catalog"."default",
  "label_cnt" int4,
  "tag" varchar(50) COLLATE "pg_catalog"."default",
  "label" varchar(50) COLLATE "pg_catalog"."default",
  "type" int2,
  "day" varchar(10) COLLATE "pg_catalog"."default",
  "create_time" timestamp(6) DEFAULT now(),
  CONSTRAINT "mobile_day_flow_tag_pkey" PRIMARY KEY ("id")
)
WITH (fillfactor=80)
;

ALTER TABLE "public"."mobile_day_flow_tag" 
  OWNER TO "postgres";

COMMENT ON COLUMN "public"."mobile_day_flow_tag"."label_cnt" IS '人数';

COMMENT ON COLUMN "public"."mobile_day_flow_tag"."tag" IS '标签类别，例如省外来源，省内来源，性别，年龄等';

COMMENT ON COLUMN "public"."mobile_day_flow_tag"."label" IS '标签名称，例如标签类别为省内来源时，标签名称为“珠海”';

COMMENT ON COLUMN "public"."mobile_day_flow_tag"."type" IS '1=日驻留、2=新流入、3=新流出';
珠海高新区年末常驻人口信息表:
CREATE TABLE "public"."pl_pop_trend_of_end_year" (
  "date_time" varchar(10) COLLATE "pg_catalog"."default" NOT NULL,
  "num" float4,
  "create_time" timestamp(6) DEFAULT now(),
  CONSTRAINT "pl_pop_trend_of_end_year_pkey" PRIMARY KEY ("date_time")
)
WITH (fillfactor=80)
;

ALTER TABLE "public"."pl_pop_trend_of_end_year" 
  OWNER TO "postgres";
COMMENT ON COLUMN "public"."pl_pop_trend_of_end_year"."num" IS '单位(万)';
COMMENT ON TABLE "public"."pl_pop_trend_of_end_year" IS '年末常驻人口变化趋势';
珠海高新区各社区人口年龄分布统计结果表:
CREATE TABLE "public"."grid_first_level_info" (
  "community" varchar(30) COLLATE "pg_catalog"."default" NOT NULL,
  "grid_leader" varchar(1000) COLLATE "pg_catalog"."default",
  "build_num" int4 DEFAULT 0,
  "population" int4 DEFAULT 0,
  "inconvenience_num" int4 DEFAULT 0,
  "disable_num" int4 DEFAULT 0,
  "other_pop_num" int4 DEFAULT 0,
  "geom" geometry(GEOMETRY),
  "overview" varchar(500) COLLATE "pg_catalog"."default",
  "area" float4,
  "resident_population" int4,
  "registered_population" int4,
  "total_population" int4,
  "location" varchar(50) COLLATE "pg_catalog"."default",
  "mac" varchar(255) COLLATE "pg_catalog"."default",
  CONSTRAINT "grid_first_level_info_new_pkey" PRIMARY KEY ("community")
)
WITH (fillfactor=80)
;

ALTER TABLE "public"."grid_first_level_info" 
  OWNER TO "postgres";

COMMENT ON COLUMN "public"."grid_first_level_info"."community" IS '社区';

COMMENT ON COLUMN "public"."grid_first_level_info"."grid_leader" IS '网格长信息';

COMMENT ON COLUMN "public"."grid_first_level_info"."build_num" IS '楼栋数';

COMMENT ON COLUMN "public"."grid_first_level_info"."population" IS '人数';

COMMENT ON COLUMN "public"."grid_first_level_info"."inconvenience_num" IS '行动不便人数';

COMMENT ON COLUMN "public"."grid_first_level_info"."disable_num" IS '残疾人人数';

COMMENT ON COLUMN "public"."grid_first_level_info"."other_pop_num" IS '港澳台外籍人数';

COMMENT ON COLUMN "public"."grid_first_level_info"."geom" IS '地理信息';

COMMENT ON COLUMN "public"."grid_first_level_info"."overview" IS '概况';

COMMENT ON COLUMN "public"."grid_first_level_info"."area" IS '社区面积（平方公里）';

COMMENT ON COLUMN "public"."grid_first_level_info"."resident_population" IS '常住人口';

COMMENT ON COLUMN "public"."grid_first_level_info"."registered_population" IS '户籍人口';

COMMENT ON COLUMN "public"."grid_first_level_info"."total_population" IS '总居住人口';

COMMENT ON COLUMN "public"."grid_first_level_info"."location" IS '中心坐标';

COMMENT ON COLUMN "public"."grid_first_level_info"."mac" IS 'grid_leader字段的mac值';

COMMENT ON TABLE "public"."grid_first_level_info" IS '一级社区网格信息';
"""
        "The SQL query must be formatted in Markdown as follows:\n\n"
        "```sql\n"
        "SELECT * FROM table_name;\n"
        "```"
    )

    for attempt in range(retry_count):
        # 调用AI模型生成SQL语句
        ai_response = call_qwen_model(model_type, system_prompt, user_input)

        if ai_response:
            # 从AI的回复中提取SQL语句
            sql_start = ai_response.find("```sql\n") + len("```sql\n")
            sql_end = ai_response.find("\n```", sql_start)
            sql_query = ai_response[sql_start:sql_end].strip()
            
            if sql_query:
                return sql_query
            else:
                logging.warning(f"第 {attempt + 1} 次尝试未能从AI的回复中提取SQL语句")
        else:
            logging.warning(f"第 {attempt + 1} 次尝试AI未能生成有效的回复")

    logging.error("多次尝试后仍未能生成SQL语句")
    return None


def execute_sql_query(sql_query, retry_count=3):
    """
    执行SQL查询并返回结果。

    :param sql_query: 要执行的SQL查询
    :param retry_count: 重试次数
    :return: 查询结果的Pandas DataFrame或None
    """
    conn = None
    for attempt in range(retry_count):
        try:
            # 从环境变量中获取数据库连接信息
            dbname = "chabi_template"
            user = "aigcgen"
            password = 'Louis!123456'
            host = "127.0.0.1"
            port = "5433"

            # 连接到PostgreSQL数据库
            conn = psycopg2.connect(
                dbname=dbname,
                user=user,
                password=password,
                host=host,
                port=port
            )
            # 执行SQL查询
            df = pd.read_sql_query(sql_query, conn)
            return df
        except Exception as e:
            logging.error(f"SQL查询错误: {e}")
            if attempt < retry_count - 1:
                logging.info("重新生成SQL查询语句并重试...")
                user_input = "获取所有用户的姓名和邮箱"  # 示例用户输入
                sql_query = analyze_user_intent_and_generate_sql(user_input)
                if not sql_query:
                    logging.error("重新生成SQL查询语句失败")
                    return None
            else:
                logging.error("多次尝试后仍未能成功执行SQL查询")
                return None
        finally:
            if conn:
                conn.close()

def refine_data_with_ai(user_input, df):
    """
    使用AI模型对查询结果数据进行梳理整理。

    :param user_input: 用户的输入
    :param df: 查询结果的Pandas DataFrame
    :return: 梳理整理后的数据（JSON格式）
    """
    system_prompt = (
        "Based on the user's question and the query result, organize and refine the data. "
        "The refined data should be consistent with the original data and returned in JSON format using markdown."
        "User's question: {user_input}\n\n"
        "Query result:\n{query_result}"
    )
    query_result = df.to_json(orient='records')
    final_prompt = system_prompt.format(user_input=user_input, query_result=query_result)
    print("系统提示词:\n", final_prompt)  # 打印最终的系统提示词
    ai_response = call_qwen_model(model_type, final_prompt)

    if ai_response:
        try:
            # 提取Markdown中的JSON数据
            json_start = ai_response.find("```json\n") + len("```json\n")
            json_end = ai_response.find("\n```", json_start)
            json_data = ai_response[json_start:json_end].strip()
            
            # 解析JSON数据
            refined_data = json.loads(json_data)
            return refined_data
        except (ValueError, AttributeError) as e:
            logging.error(f"无法解析AI返回的数据为JSON格式: {e}")
            return None
    else:
        logging.error("无法从AI的回复中提取梳理整理后的数据")
        return None
    
def determine_chart_type(user_input):
    """
    根据用户输入判断生成的图表类型。

    :param user_input: 用户的输入
    :return: 图表类型（'line', 'pie', 'histogram'）
    """
    user_input = user_input.lower()
    if "趋势" in user_input or "变化" in user_input:
        return 'line'
    elif "分布" in user_input or "比例" in user_input:
        return 'pie'
    elif "频率" in user_input or "直方图" in user_input:
        return 'histogram'
    else:
        return 'line'  # 默认生成折线图    

# def generate_line_chart_from_json(json_data):
#     """
#     使用Plotly从JSON数据生成折线图。

#     :param json_data: JSON格式的数据
#     :return: JSON格式的图表数据
#     """
#     # 将JSON数据转换为Pandas DataFrame
#     df = pd.read_json(StringIO(json.dumps(json_data)))

#     # 动态获取列名
#     x_column = df.columns[0]
#     y_column = df.columns[1]

#     # 生成折线图
#     fig = px.line(df, x=x_column, y=y_column, title='动态生成的折线图')

#     # 将图表渲染为JSON格式
#     chart_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
#     return chart_json
   
def generate_line_chart_from_df(df, output_file, x_column, y_column):
    """
    使用Plotly从DataFrame生成折线图并保存为图片。

    :param df: Pandas DataFrame格式的数据
    :param output_file: 保存图片的文件路径
    :param x_column: X轴数据列名
    :param y_column: Y轴数据列名
    """
    # 生成折线图
    fig = px.line(df, x=x_column, y=y_column, title='动态生成的折线图')

    # 保存图表为图片
    pio.write_image(fig, output_file)
                
# def generate_pie_chart_from_json(json_data):
#     """
#     使用Plotly从JSON数据生成饼图。

#     :param json_data: JSON格式的数据
#     :return: JSON格式的图表数据
#     """
#     # 将JSON数据转换为Pandas DataFrame
#     df = pd.read_json(StringIO(json.dumps(json_data)))

#     # 动态获取列名
#     names_column = df.columns[0]
#     values_column = df.columns[1]

#     # 生成饼图
#     fig = px.pie(df, names=names_column, values=values_column, title='动态生成的饼图')

#     # 将图表渲染为JSON格式
#     chart_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
#     return chart_json

def generate_pie_chart_from_df(df, output_file, names_column, values_column):
    """
    使用Plotly从DataFrame生成饼图并保存为图片。

    :param df: Pandas DataFrame格式的数据
    :param output_file: 保存图片的文件路径
    :param names_column: 名称数据列名
    :param values_column: 值数据列名
    """
    # 生成饼图
    fig = px.pie(df, names=names_column, values=values_column, title='动态生成的饼图')

    # 保存图表为图片
    pio.write_image(fig, output_file)

# def generate_histogram_from_json(json_data):
#     """
#     使用Plotly从JSON数据生成直方图。

#     :param json_data: JSON格式的数据
#     :return: JSON格式的图表数据
#     """
#     # 将JSON数据转换为Pandas DataFrame
#     df = pd.read_json(StringIO(json.dumps(json_data)))

#     # 动态获取列名
#     x_column = df.columns[0]

#     # 生成直方图
#     fig = px.histogram(df, x=x_column, title='动态生成的直方图')

#     # 将图表渲染为JSON格式
#     chart_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
#     return chart_json

def generate_histogram_from_df(df, output_file, x_column):
    """
    使用Plotly从DataFrame生成直方图并保存为图片。

    :param df: Pandas DataFrame格式的数据
    :param output_file: 保存图片的文件路径
    :param x_column: X轴数据列名
    """
    # 生成直方图
    fig = px.histogram(df, x=x_column, title='动态生成的直方图')

    # 保存图表为图片
    pio.write_image(fig, output_file)

if __name__ == "__main__":
    # 记录开始时间
    start_time = time.time()
    user_input = "2024年10月人口进出趋势变化"
    
    # 确定图表类型
    chart_type = determine_chart_type(user_input)
    logging.info(f"确定的图表类型: {chart_type}")
    
    # 记录生成SQL语句的开始时间
    sql_start_time = time.time()
    sql_query = analyze_user_intent_and_generate_sql(user_input)
    sql_end_time = time.time()
    
    if sql_query:
        # 记录执行SQL查询的开始时间
        query_start_time = time.time()
        df = execute_sql_query(sql_query)
        logging.info(f"数据库查询结果：\n{df}")
        query_end_time = time.time()
        
        if df is not None:
            # refined_df = refine_data_with_ai(user_input, df)
            if df is not None:
                # # print("梳理整理后的数据:")
                # # print(refined_df)
                
                # # 根据图表类型生成相应的图表并渲染为JSON
                # if chart_type == 'line':
                #     chart_json = generate_line_chart_from_json(df)
                # elif chart_type == 'pie':
                #     chart_json = generate_pie_chart_from_json(df)
                # elif chart_type == 'histogram':
                #     chart_json = generate_histogram_from_json(df)
                
                # print(f"生成的{chart_type}图JSON:")
                # print(chart_json)
                # 获取X轴和Y轴的列名
                x_column = df.columns[0]
                y_column = df.columns[1] if len(df.columns) > 1 else None
                
                output_file = f"{chart_type}_chart.png"
                if chart_type == 'line':
                    generate_line_chart_from_df(df, output_file, x_column, y_column)
                elif chart_type == 'pie':
                    generate_pie_chart_from_df(df, output_file, x_column, y_column)
                elif chart_type == 'histogram':
                    generate_histogram_from_df(df, output_file, x_column)
                    
                    
                print(f"生成的{chart_type}图已保存为图片: {output_file}")
            else:
                print("未能梳理整理数据")
        else:
            print("SQL查询失败")
    else:
        print("未能生成SQL语句")
        # 记录结束时间
    end_time = time.time()
    elapsed_time = end_time - start_time
    sql_generation_time = sql_end_time - sql_start_time
    sql_query_time = query_end_time - query_start_time
    
    logging.info(f"\n\n程序开始时间: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_time))}\n")
    logging.info(f"程序结束时间: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(end_time))}")
    logging.info(f"程序总运行时间: {elapsed_time:.2f} 秒")
    logging.info(f"生成SQL语句时间: {sql_generation_time:.2f} 秒")
    logging.info(f"执行SQL查询时间: {sql_query_time:.2f} 秒")
    
        