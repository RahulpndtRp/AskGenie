# app/services/functions.py

from typing import Dict, Any
from app.core.logger import logger
import httpx

# Function schema definitions (OpenAI format)
FUNCTIONS = [
    {
        "name": "search_location",
        "description": "Finds the location details based on a place name.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Location or place to search for, e.g., 'Eiffel Tower Paris'",
                }
            },
            "required": ["query"],
        },
    },
    {
        "name": "search_shopping",
        "description": "Finds shopping items related to a product query.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Product name to search for shopping, e.g., 'iPhone 15 Pro'",
                }
            },
            "required": ["query"],
        },
    },
    {
        "name": "get_stock_info",
        "description": "Fetches stock market information for a given ticker symbol.",
        "parameters": {
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string",
                    "description": "Stock symbol, e.g., 'AAPL', 'TSLA', 'GOOG'",
                }
            },
            "required": ["symbol"],
        },
    },
    {
        "name": "search_news",
        "description": "Finds the latest news articles for a topic.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Topic to search news about, e.g., 'Artificial Intelligence'",
                }
            },
            "required": ["query"],
        },
    },
]

# Function call handlers
async def handle_function_call(name: str, arguments: Dict[str, Any]) -> str:
    try:
        if name == "search_location":
            return await search_location(arguments["query"])
        elif name == "search_shopping":
            return await search_shopping(arguments["query"])
        elif name == "get_stock_info":
            return await get_stock_info(arguments["symbol"])
        elif name == "search_news":
            return await search_news(arguments["query"])
        else:
            logger.error(f"[Function Handler] Unknown function called: {name}")
            return "Unknown function."
    except Exception as e:
        logger.error(f"[Function Handler] Error during function execution: {e}")
        return "Error during function execution."

# Actual function implementations

# async def search_location(query: str) -> str:
#     """Simulated search location."""
#     return f"You can find '{query}' on Google Maps."


import urllib.parse


async def search_location(query: str) -> dict:
    """
    Real Google Maps search link generator.
    Returns structured JSON with map URL.
    """
    try:
        logger.info(f"[Function] Searching Google Maps location for: {query}")
        encoded_query = urllib.parse.quote_plus(query)
        maps_url = f"https://www.google.com/maps/search/?api=1&query={encoded_query}"

        return {
            "query": query,
            "maps_url": maps_url
        }
    except Exception as e:
        logger.error(f"[search_location] Error generating Google Maps link: {e}")
        return {
            "error": "Error generating Google Maps link."
        }


# async def search_shopping(query: str) -> str:
#     """Search shopping items via Serper Shopping API."""
#     try:
#         from app.core.config import settings
#         url = "https://google.serper.dev/shopping"
#         payload = {"q": query}
#         headers = {
#             "X-API-KEY": settings.serper_api_key,
#             "Content-Type": "application/json",
#         }
#         async with httpx.AsyncClient() as client:
#             response = await client.post(url, headers=headers, json=payload, timeout=10)
#             data = response.json()
#             if "shopping" in data and len(data["shopping"]) > 0:
#                 top_product = data["shopping"][0]
#                 return f"Top product: {top_product['title']} - {top_product['link']}"
#             else:
#                 return "No shopping results found."
#     except Exception as e:
#         logger.error(f"[search_shopping] Error: {e}")
#         return "Error fetching shopping results."
    

async def search_shopping(query: str) -> dict:
    """
    Search shopping items via Serper Shopping API.
    Returns structured JSON with top product details.
    """
    try:
        from app.core.config import settings
        url = "https://google.serper.dev/shopping"
        payload = {"q": query}
        headers = {
            "X-API-KEY": settings.serper_api_key,
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=payload, timeout=10)
            data = response.json()

            if "shopping" in data and len(data["shopping"]) > 0:
                top_product = data["shopping"][0]
                return {
                    "title": top_product.get("title"),
                    "price": top_product.get("price", "N/A"),
                    "link": top_product.get("link"),
                    "image_url": top_product.get("imageUrl", None),
                }
            else:
                return {
                    "error": "No shopping results found."
                }
    except Exception as e:
        logger.error(f"[search_shopping] Error: {e}")
        return {
            "error": "Error fetching shopping results."
        }


async def get_stock_info(symbol: str) -> str:
    """Get stock info using TradingView free widget."""
    return f"You can view live stock price for {symbol} at https://www.tradingview.com/symbols/{symbol.upper()}/"



async def search_news(query: str, top_k: int = 1) -> dict:
    """
    Search latest news via Serper News API.
    Returns structured JSON with top K news articles.
    """
    try:
        from app.core.config import settings
        url = "https://google.serper.dev/news"
        payload = {"q": query}
        headers = {
            "X-API-KEY": settings.serper_api_key,
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=payload, timeout=10)
            data = response.json()

            if "news" in data and len(data["news"]) > 0:
                articles = []
                for article in data["news"][:top_k]:
                    articles.append({
                        "title": article.get("title"),
                        "source": article.get("source", "Unknown"),
                        "date": article.get("date", "N/A"),
                        "link": article.get("link"),
                        "snippet": article.get("snippet", ""),
                    })
                return {"articles": articles}
            else:
                return {
                    "articles": [],
                    "error": "No news articles found."
                }
    except Exception as e:
        logger.error(f"[search_news] Error: {e}")
        return {
            "articles": [],
            "error": "Error fetching news results."
        }
