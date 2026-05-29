"""
DeepSeek LLM 调用封装（OpenAI 兼容格式，支持流式输出）
"""
import requests
import json
import streamlit as st

# DeepSeek API 配置（从 Streamlit secrets 读取，不硬编码密钥）
DEEPSEEK_API_KEY = st.secrets.get("DEEPSEEK_API_KEY", "")
DEEPSEEK_BASE_URL = st.secrets.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")
DEEPSEEK_MODEL = st.secrets.get("DEEPSEEK_MODEL", "deepseek-chat")


def parse_response(result):
    """解析 DeepSeek API 响应（标准 OpenAI 格式）"""
    if not result:
        raise Exception("API 返回空响应")
    if "choices" in result and result["choices"]:
        choice = result["choices"][0]
        if "message" in choice and choice["message"]:
            content = choice["message"].get("content")
            if content:
                return content.strip()
            raise Exception(f"choices[0].message.content 为空: {choice}")
        raise Exception(f"choices[0] 没有 message 字段: {choice}")
    raise Exception(f"无法解析响应格式: {result}")


def _call_api(messages, model=None, temperature=0.7, max_tokens=4096):
    """非流式 API 调用"""
    model = model or DEEPSEEK_MODEL
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens
    }
    try:
        response = requests.post(
            f"{DEEPSEEK_BASE_URL}/chat/completions",
            headers=headers,
            json=payload,
            timeout=120
        )
        response.raise_for_status()
        return parse_response(response.json())
    except requests.exceptions.Timeout:
        raise ConnectionError("LLM 调用超时，请检查网络连接")
    except requests.exceptions.RequestException as e:
        raise ConnectionError(f"LLM API 请求失败: {str(e)}")
    except Exception as e:
        raise ConnectionError(f"LLM 调用失败: {str(e)}")


def _call_api_stream(messages, model=None, temperature=0.7, max_tokens=4096):
    """流式 API 调用 - 返回生成器，逐字输出"""
    model = model or DEEPSEEK_MODEL
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": True
    }
    try:
        response = requests.post(
            f"{DEEPSEEK_BASE_URL}/chat/completions",
            headers=headers,
            json=payload,
            timeout=120,
            stream=True
        )
        response.raise_for_status()
        for line in response.iter_lines():
            if line:
                line = line.decode("utf-8")
                if line.startswith("data: "):
                    data = line[6:]
                    if data == "[DONE]":
                        break
                    try:
                        chunk = json.loads(data)
                        if "choices" in chunk and chunk["choices"]:
                            delta = chunk["choices"][0].get("delta", {})
                            content = delta.get("content", "")
                            if content:
                                yield content
                    except json.JSONDecodeError:
                        continue
    except requests.exceptions.Timeout:
        raise ConnectionError("LLM 调用超时，请检查网络连接")
    except requests.exceptions.RequestException as e:
        raise ConnectionError(f"LLM API 请求失败: {str(e)}")
    except Exception as e:
        raise ConnectionError(f"LLM 调用失败: {str(e)}")


def call_llm(prompt: str, model: str = None, temperature: float = 0.7, max_tokens: int = 4096) -> str:
    return _call_api(
        [{"role": "user", "content": prompt}],
        model, temperature, max_tokens
    )


def call_llm_with_system(system_prompt: str, user_prompt: str, model: str = None) -> str:
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": user_prompt})
    return _call_api(messages, model)


def call_llm_stream(system_prompt: str, user_prompt: str, model: str = None):
    """流式调用 LLM，返回生成器。适合 st.write_stream() 使用。"""
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": user_prompt})
    return _call_api_stream(messages, model)
