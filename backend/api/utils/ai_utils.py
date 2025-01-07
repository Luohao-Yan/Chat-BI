import os
import json
import logging
import requests
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 从环境变量中获取API URL
api_url_14b_chat = os.getenv("API_URL_14B_CHAT")
api_url_14b_generate = os.getenv("API_URL_14B_GENERATE")
api_url_72b_chat = os.getenv("API_URL_72B_CHAT")

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
        "api_url": api_url_14b_chat,
        "model": "qwen2.5:14b",
        "call_function": "call_qwen_chat_14B_api",
    },
    "14B-generate": {
        "api_url": api_url_14b_generate,
        "model": "qwen2.5:14b",
        "call_function": "call_qwen_generate_14B_api",
    },
    "72B-chat": {
        "api_url": api_url_72b_chat,
        "model": "/root/.cache/modelscope",
        "call_function": "call_qwen_chat_72B_api",
    },
}

async def make_api_request(api_url, headers, data):
    try:
        response = await session.post(api_url, headers=headers, data=json.dumps(data), timeout=120)
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

async def call_qwen_chat_14B_api(api_url, model, system_prompt, user_input):
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
    result = await make_api_request(api_url, headers, data)
    if result and "message" in result and "content" in result["message"]:
        return result["message"]["content"]
    else:
        logging.error("API响应中没有预期的'message'或'content'字段")
        return None

async def call_qwen_generate_14B_api(api_url, model, system_prompt):
    headers = {"Content-Type": "application/json"}
    data = {
        "model": model,
        "prompt": system_prompt,
        "stream": False,
    }
    result = await make_api_request(api_url, headers, data)
    if result and "response" in result:
        return result["response"]
    else:
        logging.error("API响应中没有预期的'response'字段")
        return None

async def call_qwen_chat_72B_api(api_url, model, system_prompt, user_input=None):
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
    result = await make_api_request(api_url, headers, data)
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

async def call_qwen_model(model_type, system_prompt, user_input=None):
    config = model_config.get(model_type)
    if not config:
        logging.error("未知的模型类型")
        return None

    api_url = config["api_url"]
    model = config["model"]
    call_function = config["call_function"]

    if call_function == "call_qwen_chat_14B_api":
        return await call_qwen_chat_14B_api(api_url, model, system_prompt, user_input)
    elif call_function == "call_qwen_generate_14B_api":
        return await call_qwen_generate_14B_api(api_url, model, system_prompt)
    elif call_function == "call_qwen_chat_72B_api":
        return await call_qwen_chat_72B_api(api_url, model, system_prompt, user_input)
    else:
        logging.error("未知的调用函数")
        return None

async def analyze_user_intent_and_generate_sql(user_input, retry_count=3):
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
        ai_response = await call_qwen_model(model_type, system_prompt, user_input)

        if ai_response:
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

async def refine_data_with_ai(user_input, df):
    system_prompt = (
        "Based on the user's question and the query result, determine the appropriate columns for the X-axis and Y-axis, "
        "as well as the scale and unit for displaying the data. The column names, scale, and unit should be returned in JSON format using markdown.\n\n"
        "User's question: {user_input}\n\n"
        "Query result:\n\n"
        f"{df.to_json(orient='records')}\n\n"
        "The JSON format should be as follows:\n\n"
        "```json\n"
        "{\n"
        '  "x_axis": "column_name",\n'
        '  "y_axis": "column_name",\n'
        '  "scale": "linear",\n'
        '  "unit": "unit_name"\n'
        "}\n"
        "```"
    )

    ai_response = await call_qwen_model(model_type, system_prompt, user_input)
    if ai_response:
        json_start = ai_response.find("```json\n") + len("```json\n")
        json_end = ai_response.find("\n```", json_start)
        json_data = ai_response[json_start:json_end].strip()
        
        try:
            refined_data = json.loads(json_data)
            return refined_data
        except json.JSONDecodeError as e:
            logging.error(f"JSON解析错误: {e}")
            return None
    else:
        logging.error("AI未能生成有效的回复")
        return None

async def determine_chart_type(user_input, json_data):
    system_prompt = (
        "Based on the user's question and the provided data, determine the most appropriate chart type to visualize the data. "
        "The chart type should be returned as a string in markdown format.\n\n"
        "User's question: {user_input}\n\n"
        "Data:\n\n"
        f"{json_data}\n\n"
        "The chart type should be one of the following: 'bar', 'line', 'pie', 'scatter', 'histogram'.\n\n"
        "The response should be formatted as follows:\n\n"
        "```chart\n"
        "chart_type\n"
        "```"
    )

    ai_response = await call_qwen_model(model_type, system_prompt, user_input)
    if ai_response:
        chart_start = ai_response.find("```chart\n") + len("```chart\n")
        chart_end = ai_response.find("\n```", chart_start)
        chart_type = ai_response[chart_start:chart_end].strip()
        
        if chart_type in ['bar', 'line', 'pie', 'scatter', 'histogram']:
            return chart_type
        else:
            logging.error("AI生成的图表类型无效")
            return None
    else:
        logging.error("AI未能生成有效的回复")
        return None