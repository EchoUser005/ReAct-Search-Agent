import os
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()


def get_llm(temperature: float = 0.5):
    """获取 LLM 实例"""

    return ChatOpenAI(
        base_url=os.getenv("QWEN_BASE_URL"),
        api_key=os.getenv("QWEN_API_KEY"),
        model="qwen-plus",
        temperature=temperature,
        max_tokens=4096
    )
