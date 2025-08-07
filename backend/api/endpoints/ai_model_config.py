from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
import json
import os
import logging
import time
import aiohttp
import asyncio
from pathlib import Path

router = APIRouter()

class ModelConfig(BaseModel):
    apiKey: str = Field(..., description="API密钥")
    baseUrl: str = Field(..., description="API基础地址") 
    model: str = Field(..., description="模型名称")
    temperature: float = Field(default=0.7, ge=0, le=2, description="温度参数")
    maxTokens: int = Field(default=2000, ge=100, le=4000, description="最大token数")

class SaveConfigRequest(BaseModel):
    provider: str = Field(..., description="模型提供商")
    config: ModelConfig = Field(..., description="模型配置")

class TestConfigRequest(BaseModel):
    config: ModelConfig = Field(..., description="待测试的配置")
    message: str = Field(..., description="测试消息")

class AIConfigResponse(BaseModel):
    provider: Optional[str] = None
    config: Optional[ModelConfig] = None

# 配置文件路径
CONFIG_DIR = Path(__file__).parent.parent.parent / "config"
CONFIG_FILE = CONFIG_DIR / "ai_model_config.json"

def ensure_config_dir():
    """确保配置目录存在"""
    CONFIG_DIR.mkdir(exist_ok=True)

def load_config() -> Dict[str, Any]:
    """加载配置"""
    ensure_config_dir()
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"加载配置失败: {e}")
    return {}

def save_config(config_data: Dict[str, Any]):
    """保存配置"""
    ensure_config_dir()
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logging.error(f"保存配置失败: {e}")
        raise HTTPException(status_code=500, detail=f"保存配置失败: {str(e)}")

@router.get("/ai-config", response_model=AIConfigResponse)
async def get_ai_config():
    """获取当前AI模型配置"""
    try:
        config_data = load_config()
        return AIConfigResponse(**config_data)
    except Exception as e:
        logging.error(f"获取配置失败: {e}")
        return AIConfigResponse()

@router.post("/ai-config/save")
async def save_ai_config(request: SaveConfigRequest):
    """保存AI模型配置"""
    try:
        config_data = {
            "provider": request.provider,
            "config": request.config.dict()
        }
        save_config(config_data)
        logging.info(f"AI模型配置已保存: provider={request.provider}")
        return {"message": "配置保存成功"}
    except Exception as e:
        logging.error(f"保存配置失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/ai-config/test")
async def test_ai_config(request: TestConfigRequest):
    """测试AI模型配置"""
    start_time = time.time()
    
    try:
        # 构建请求头
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {request.config.apiKey}"
        }
        
        # 构建请求体
        data = {
            "model": request.config.model,
            "messages": [
                {
                    "role": "user",
                    "content": request.message
                }
            ],
            "temperature": request.config.temperature,
            "max_tokens": request.config.maxTokens
        }
        
        # 发送异步HTTP请求
        timeout = aiohttp.ClientTimeout(total=30)  # 30秒超时
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(request.config.baseUrl, json=data, headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    end_time = time.time()
                    response_time = int((end_time - start_time) * 1000)
                    
                    # 检查响应格式
                    if 'choices' in result and len(result['choices']) > 0:
                        return {
                            "success": True,
                            "responseTime": response_time,
                            "message": "连接测试成功",
                            "response": result['choices'][0]['message']['content'][:100] + "..." if len(result['choices'][0]['message']['content']) > 100 else result['choices'][0]['message']['content']
                        }
                    else:
                        return {
                            "success": False,
                            "message": "响应格式异常",
                            "details": str(result)
                        }
                else:
                    error_text = await response.text()
                    return {
                        "success": False,
                        "message": f"HTTP {response.status}: {error_text}"
                    }
                    
    except asyncio.TimeoutError:
        return {
            "success": False,
            "message": "请求超时，请检查网络连接或API地址"
        }
    except aiohttp.ClientError as e:
        return {
            "success": False,
            "message": f"网络请求失败: {str(e)}"
        }
    except Exception as e:
        logging.error(f"测试AI配置失败: {e}")
        return {
            "success": False,
            "message": f"测试失败: {str(e)}"
        }

async def get_current_ai_config() -> Optional[Dict[str, Any]]:
    """获取当前生效的AI配置（供其他模块使用）"""
    try:
        config_data = load_config()
        if config_data and 'config' in config_data:
            return config_data['config']
        return None
    except Exception as e:
        logging.error(f"获取当前AI配置失败: {e}")
        return None

async def call_ai_model(message: str, config: Optional[Dict[str, Any]] = None) -> Optional[str]:
    """调用AI模型（供其他模块使用）"""
    if not config:
        config = await get_current_ai_config()
        
    if not config:
        logging.error("没有可用的AI配置")
        return None
        
    try:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {config['apiKey']}"
        }
        
        data = {
            "model": config['model'],
            "messages": [
                {
                    "role": "user",
                    "content": message
                }
            ],
            "temperature": config.get('temperature', 0.7),
            "max_tokens": config.get('maxTokens', 2000)
        }
        
        timeout = aiohttp.ClientTimeout(total=30)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(config['baseUrl'], json=data, headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    if 'choices' in result and len(result['choices']) > 0:
                        return result['choices'][0]['message']['content']
                else:
                    error_text = await response.text()
                    logging.error(f"AI调用失败: HTTP {response.status}: {error_text}")
                    
    except Exception as e:
        logging.error(f"调用AI模型失败: {e}")
        
    return None