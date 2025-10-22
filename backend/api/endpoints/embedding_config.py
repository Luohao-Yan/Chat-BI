"""
Embedding 模型配置 API
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import logging
import os
from pathlib import Path

router = APIRouter()
logger = logging.getLogger(__name__)

# 配置文件路径
CONFIG_FILE = Path(__file__).parent.parent.parent / ".env"


class EmbeddingConfig(BaseModel):
    model: str
    api_key: Optional[str] = None
    dimension: int


@router.get("/embedding-config")
async def get_embedding_config():
    """
    获取当前 Embedding 配置

    Returns:
        当前的 embedding 模型配置
    """
    try:
        from core.config import settings

        return {
            "model": settings.EMBEDDING_MODEL,
            "api_key": settings.OPENAI_API_KEY if settings.OPENAI_API_KEY else "",
            "dimension": settings.EMBEDDING_DIMENSION
        }
    except Exception as e:
        logger.error(f"获取 Embedding 配置失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取配置失败: {str(e)}")


@router.post("/embedding-config")
async def update_embedding_config(config: EmbeddingConfig):
    """
    更新 Embedding 配置

    Args:
        config: 新的 embedding 配置

    Returns:
        更新结果
    """
    try:
        # 读取现有 .env 文件
        env_content = {}
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        env_content[key.strip()] = value.strip()

        # 更新配置
        env_content['EMBEDDING_MODEL'] = config.model
        env_content['EMBEDDING_DIMENSION'] = str(config.dimension)
        if config.api_key:
            env_content['OPENAI_API_KEY'] = config.api_key

        # 写回 .env 文件
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            for key, value in env_content.items():
                f.write(f"{key}={value}\n")

        logger.info(f"Embedding 配置已更新: {config.model} ({config.dimension}维)")

        return {
            "success": True,
            "message": "配置已保存，重启服务器后生效",
            "config": {
                "model": config.model,
                "dimension": config.dimension
            }
        }
    except Exception as e:
        logger.error(f"更新 Embedding 配置失败: {e}")
        raise HTTPException(status_code=500, detail=f"保存配置失败: {str(e)}")
