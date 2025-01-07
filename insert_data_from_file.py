import os
import psycopg2
import logging
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 配置日志记录
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# 从环境变量中获取数据库连接信息
dbname = os.getenv("DBNAME")
user = os.getenv("DBUSER", "aigcgen")
password = os.getenv("DBPGPASSWORD")
host = os.getenv("DBHOST")
port = os.getenv("DBPORT")

# 打印环境变量以确认加载正确
logging.info(f"数据库名: {dbname}")
logging.info(f"用户: {user}")
logging.info(f"主机: {host}")
logging.info(f"端口: {port}")

# 读取SQL文件内容
def read_sql_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

# 增加数据库连接测试函数
def test_db_connection():
    try:
        conn = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port
        )
        conn.close()
        logging.info("数据库连接成功")
    except Exception as e:
        logging.error(f"数据库连接失败: {e}")

def insert_data_from_file(file_path):
    conn = None
    try:
        # 连接到PostgreSQL数据库
        conn = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port
        )
        cur = conn.cursor()
        
        # 读取SQL文件内容
        sql_content = read_sql_file(file_path)
        
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

if __name__ == "__main__":
    # 测试数据库连接
    test_db_connection()
    
    # 指定SQL文件路径
    sql_file_path = '/Users/yanluohao/开发/chatbi-poc/人口流动数据.sql'
    insert_data_from_file(sql_file_path)