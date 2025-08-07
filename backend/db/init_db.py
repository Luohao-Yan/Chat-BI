import os
import logging
import json
import inspect
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.sql import text
from models.generate_chart_models import Base
from db.session import engine, async_session  # 导入engine和async_session
from models import generate_chart_models


def get_model_classes(module):
    """获取模块中所有的SQLAlchemy模型类"""
    return {
        name: cls
        for name, cls in inspect.getmembers(module, inspect.isclass)
        if issubclass(cls, Base) and cls.__module__ == module.__name__
    }


async def init_db():
    async with engine.begin() as conn:
        try:
            # 创建所有表
            logging.info("正在创建所有表...")
            await conn.run_sync(Base.metadata.create_all)
            logging.info("所有表创建成功")
        except SQLAlchemyError as e:
            logging.error(f"数据库操作错误: {e}")


async def insert_mock_data():
    # 获取当前文件的目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # 构建JSON文件的绝对路径
    json_files = [
        os.path.join(current_dir, "..", "mock", "人口活力.json"),
        os.path.join(current_dir, "..", "mock", "人口流动数据.json"),
    ]

    try:
        # 使用独立的会话进行数据插入
        async with async_session() as session:
            try:
                # 获取所有模型类
                model_classes = get_model_classes(generate_chart_models)

                for json_file in json_files:
                    # 从JSON文件读取mock数据
                    logging.info(f"正在读取{json_file}中的mock数据...")
                    with open(json_file, "r", encoding="utf-8") as file:
                        data_list = json.load(file)

                    # 插入mock数据
                    logging.info(f"正在插入{json_file}中的mock数据...")
                    for data in data_list:
                        table_name = data.pop("table_name", None)
                        if table_name:
                            model = model_classes.get(table_name)
                            if model:
                                # logging.info(f"正在插入数据到表 {table_name}: {data}")
                                session.add(model(**data))
                            # else:
                            # logging.warning(f"未找到表 {table_name} 对应的模型类")
                        else:
                            logging.warning("数据中缺少 table_name 字段")

                # 提交事务
                await session.commit()
                logging.info("所有mock数据插入成功")

            except SQLAlchemyError as e:
                logging.error(f"插入mock数据错误: {e}")
                await session.rollback()
                raise
            except Exception as e:
                logging.error(f"处理mock数据时发生错误: {e}")
                await session.rollback()
                raise

        # 使用新的会话进行数据验证
        async with async_session() as session:
            try:
                # 手动查询数据库以验证数据是否插入成功
                for table_name, model in model_classes.items():
                    result = await session.execute(
                        text(f"SELECT * FROM {model.__tablename__} LIMIT 1")
                    )
                    rows = result.fetchall()
                    logging.info(f"表 {table_name} 中的数据: {rows}")
            except SQLAlchemyError as e:
                logging.error(f"验证数据时发生错误: {e}")
            except Exception as e:
                logging.error(f"验证数据时发生未知错误: {e}")

    except Exception as e:
        logging.error(f"插入mock数据过程中发生错误: {e}")
        # 不重新抛出异常，让应用继续启动
