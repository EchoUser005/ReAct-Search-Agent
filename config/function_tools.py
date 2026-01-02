"""
1. 使用 bocha API 来封装 tools
"""
import os
import httpx
from dotenv import load_dotenv
from langchain_core.tools import tool
load_dotenv()

BOCHA_BASE_URL = os.getenv("BOCHA_BASE_URL", "https://api.bochaapi.com/v1/web-search")
BOCHA_API_KEY = os.getenv("BOCHA_API_KEY")


@tool
def web_search(query: str, freshness: str = "noLimit", count: int = 5) -> str:
    """
    Args:
        query: 搜索关键词，3-6个维度不重复覆盖用户完整需求的核心词，避免口语化长句和虚词。
        freshness: 时效性过滤，按用户问题所需要的时效性来选择day/week/month/year/noLimit其一。
        count: 返回结果数量，默认5，简单事实3-5条，复杂信息搜集5-10条。
    """
    try:
        resp = httpx.post(
            BOCHA_BASE_URL,
            headers={"Authorization": f"Bearer {BOCHA_API_KEY}"},
            json={"query": query, "freshness": freshness, "count": count},
            timeout=60
        )
        data = resp.json()

        results = []
        for item in data.get("data", {}).get("webPages", {}).get("value", []):
            results.append(f"[{item['name']}]({item['url']})\n{item['snippet']}")

        return "\n\n".join(results) if results else "未找到相关结果"
    except Exception as e:
        return f"搜索失败: {str(e)}"


@tool
def tool_current_location() -> str:
    """获取用户当前位置"""
    location = {
        "lng": 114.055586,
        "lat": 22.546713
    }
    return f"{location['lng']},{location['lat']},深圳市,市民中心"