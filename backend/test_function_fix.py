#!/usr/bin/env python3
"""
测试函数调用功能的修复
"""

import requests
import json
import time


def test_insight_analysis_api():
    """测试洞察分析API"""
    print("测试洞察分析API...")

    # 测试不同的用户输入
    test_inputs = ["6月的车流数据是多少？", "珠海高新区人口数据", "社区人口分布"]

    for user_input in test_inputs:
        try:
            response = requests.get(
                "http://localhost:8000/api/insight_analysis",
                params={"user_input": user_input},
                timeout=10,
            )
            print(f"输入: {user_input}")
            print(f"状态码: {response.status_code}")
            print(f"响应: {response.json()}")
            print("-" * 50)
        except Exception as e:
            print(f"测试失败: {e}")


def test_generate_chart_api():
    """测试图表生成API"""
    print("\n测试图表生成API...")

    test_inputs = [
        {"user_input": "6月的车流数据是多少？"},
        {"user_input": "珠海高新区人口数据"},
        {"user_input": "社区人口分布"},
    ]

    for user_input in test_inputs:
        try:
            response = requests.post(
                "http://localhost:8000/api/generate_chart", json=user_input, timeout=30
            )
            print(f"输入: {user_input['user_input']}")
            print(f"状态码: {response.status_code}")
            result = response.json()
            if "error" in result:
                print(f"错误: {result['error']}")
                print(f"消息: {result['message']}")
            else:
                print(f"数据条数: {len(result.get('data', []))}")
                print(f"图表类型: {result.get('chart_type', 'N/A')}")
            print("-" * 50)
        except Exception as e:
            print(f"测试失败: {e}")


def test_function_calling():
    """测试函数调用功能"""
    print("\n测试函数调用功能...")

    # 使用requests库测试函数调用
    api_base = "http://localhost:8000/v1"
    headers = {"Content-Type": "application/json", "Authorization": "Bearer none"}

    # 定义函数规范
    functions = [
        {
            "name": "get_current_weather",
            "description": "Get the current weather",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g. San Francisco, CA",
                    },
                    "format": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"],
                        "description": "The temperature unit to use. Infer this from the users location.",
                    },
                },
                "required": ["location", "format"],
            },
        }
    ]

    messages = [
        {
            "role": "system",
            "content": "Don't make assumptions about what values to plug into functions. Ask for clarification if a user request is ambiguous.",
        },
        {
            "role": "user",
            "content": "What's the weather like today in San Francisco, CA?",
        },
    ]

    try:
        payload = {"model": "Qwen", "messages": messages, "functions": functions}

        response = requests.post(
            f"{api_base}/chat/completions",
            headers=headers,
            data=json.dumps(payload),
            timeout=30,
        )

        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
        else:
            print(f"错误响应: {response.text}")

    except Exception as e:
        print(f"函数调用测试失败: {e}")


if __name__ == "__main__":
    print("开始测试函数调用功能修复...")

    # 等待服务启动
    print("等待服务启动...")
    time.sleep(2)

    # 测试洞察分析API
    test_insight_analysis_api()

    # 测试图表生成API
    test_generate_chart_api()

    # 测试函数调用功能
    test_function_calling()

    print("\n测试完成！")
