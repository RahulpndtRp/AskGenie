import httpx
from urllib.parse import quote
from pydantic import BaseModel, HttpUrl
from typing import List
from app.core.config import settings

class SearchResult(BaseModel):
    title: str
    link: HttpUrl

async def brave_search(query: str, count: int = 4) -> List[SearchResult]:
    """
    Perform a Brave web search for `query`. Returns a list of SearchResult.
    """
    url = f"https://api.search.brave.com/search?q={quote(query)}&count={count}"
    headers = {
        "Accept": "application/json",
        "Accept-Encoding": "gzip",
        "X-Subscription-Token": settings.brave_search_api_key
    }
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, headers=headers)
        resp.raise_for_status()
        data = resp.json()
    results = data.get("web", {}).get("results", [])
    return [SearchResult(title=r.get("title", ""), link=r.get("url", "")) for r in results]
import httpx
from app.core.config import settings
from app.core.logger import logger
from typing import List
from pydantic import BaseModel, HttpUrl

class SearchResult(BaseModel):
    title: str
    link: HttpUrl

async def serper_search(query: str, count: int = 4) -> List[SearchResult]:
    url = "https://google.serper.dev/search"
    headers = {
        "X-API-KEY": settings.serper_api_key,
        "Content-Type": "application/json"
    }
    payload = {"q": query}

    logger.info(f"[Serper Search] Sending request to {url}")
    logger.info(f"[Serper Search] Headers: {headers}")
    logger.info(f"[Serper Search] Payload: {payload}")

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=payload, headers=headers)
            logger.info(f"[Serper Search] Received response with status code: {response.status_code}")

            response.raise_for_status()  # This will raise HTTPStatusError if not 200

            data = response.json()
            organic = data.get("organic", [])
            logger.info(f"[Serper Search] Organic results received: {len(organic)}")

            return [SearchResult(title=item.get("title", ""), link=item.get("link", "")) for item in organic[:count]]

        except httpx.HTTPStatusError as e:
            logger.error(f"[Serper Search Error] Status Code: {e.response.status_code}")
            logger.error(f"[Serper Search Error] Response Content: {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"[Serper Search Fatal Error] {e}")
            raise
