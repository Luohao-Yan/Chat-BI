from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import json
import logging
import asyncio
import aiohttp
from api.endpoints.ai_model_config import get_current_ai_config

router = APIRouter()
logger = logging.getLogger(__name__)


class StreamInsightRequest(BaseModel):
    user_input: str
    data: str  # JSON格式的数据


@router.post("/insight_analysis_stream")
async def insight_analysis_stream(request: StreamInsightRequest):
    """流式洞察分析"""

    async def generate_stream():
        try:
            # 获取AI配置
            config = await get_current_ai_config()
            if not config:
                yield f"data: {json.dumps({'error': '未找到AI配置'})}\n\n"
                return

            # 动态获取当前时间信息
            from datetime import datetime
            import pytz
            
            # 获取中国时区的当前时间
            china_tz = pytz.timezone('Asia/Shanghai')
            current_time = datetime.now(china_tz)
            current_date = current_time.strftime('%Y-%m-%d')
            current_year = current_time.year
            current_month = current_time.month
            
            # 构建分析提示词
            system_prompt = (
                "基于用户的问题和查询结果，生成深入的洞察分析。分析应该简洁明了，并提供从数据中得出的有意义的见解。\n\n"
                f"当前时间上下文：今天是{current_date}，当前年份是{current_year}年{current_month}月\n"
                f"数据时间范围：2024年6月至12月\n\n"
                f"用户问题：{request.user_input}\n\n"
                f"查询结果：\n{request.data}\n\n"
                "请按照以下Markdown格式返回分析结果：\n\n"
                "## 📊 数据洞察分析\n\n"
                "### 🔍 关键发现\n"
                "- **核心指标**：[描述主要数据指标]\n"
                "- **数据趋势**：[描述数据变化趋势]\n"
                "- **对比分析**：[如有对比数据，进行分析]\n\n"
                "### 💡 深度解读\n"
                "[详细分析数据背后的原因和意义]\n\n"
                "### 📈 业务启示\n"
                "1. **短期影响**：[分析对当前的影响]\n"
                "2. **长期趋势**：[预测未来可能的发展]\n"
                "3. **行动建议**：[基于数据提供的建议]\n\n"
                "### 🎯 关注要点\n"
                "> [重点提醒或需要特别关注的数据点]\n\n"
                "> 如果没有获取图表数据不做分析，直接告诉客户缺少数据，不要做任何分析\n\n"
                "请确保分析内容准确、有见地，并与用户的问题紧密相关。使用中文回答。直接返回Markdown格式的分析内容，不要使用代码块包裹。"
            )

            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {config['apiKey']}",
            }

            data = {
                "model": config["model"],
                "messages": [{"role": "system", "content": system_prompt}],
                "temperature": config.get("temperature", 0.7),
                "max_tokens": config.get("maxTokens", 2000),
                "stream": True,  # 启用流式输出
            }

            timeout = aiohttp.ClientTimeout(total=60)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(
                    config["baseUrl"], json=data, headers=headers
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        yield f"data: {json.dumps({'error': f'AI调用失败: {error_text}'})}\n\n"
                        return

                    # 处理流式响应
                    async for line in response.content:
                        if line:
                            line_text = line.decode("utf-8").strip()
                            if line_text.startswith("data: "):
                                data_part = line_text[6:]  # 去掉'data: '前缀

                                if data_part == "[DONE]":
                                    yield f"data: {json.dumps({'done': True})}\n\n"
                                    break

                                try:
                                    chunk_data = json.loads(data_part)
                                    if (
                                        "choices" in chunk_data
                                        and len(chunk_data["choices"]) > 0
                                    ):
                                        choice = chunk_data["choices"][0]
                                        if (
                                            "delta" in choice
                                            and "content" in choice["delta"]
                                        ):
                                            content = choice["delta"]["content"]
                                            if content:
                                                yield f"data: {json.dumps({'content': content})}\n\n"
                                except json.JSONDecodeError:
                                    continue
                                except Exception as e:
                                    logger.error(f"处理流式数据出错: {e}")
                                    continue

        except asyncio.TimeoutError:
            yield f"data: {json.dumps({'error': '请求超时'})}\n\n"
        except Exception as e:
            logger.error(f"流式洞察分析出错: {e}")
            yield f"data: {json.dumps({'error': f'分析失败: {str(e)}'})}\n\n"

    return StreamingResponse(
        generate_stream(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
        },
    )


@router.get("/insight_analysis_stream/{user_input}")
async def insight_analysis_stream_get(user_input: str):
    """通过GET方式获取流式洞察分析"""

    async def generate_stream():
        try:
            # 从Redis获取相关数据
            from api.dependencies.dependencies import redis_client

            data_key = f"chart_data:{user_input}"
            data_json = await redis_client.get(data_key)

            if not data_json:
                yield f"data: {json.dumps({'error': '未找到相关数据'})}\n\n"
                return

            # 创建请求对象
            request = StreamInsightRequest(user_input=user_input, data=data_json)

            # 调用流式分析
            async for chunk in insight_analysis_stream(request).body_iterator:
                yield chunk

        except Exception as e:
            logger.error(f"GET流式洞察分析出错: {e}")
            yield f"data: {json.dumps({'error': f'分析失败: {str(e)}'})}\n\n"

    return StreamingResponse(
        generate_stream(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
        },
    )
