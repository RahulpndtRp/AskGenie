from redis.asyncio import from_url
from app.core.config import settings
from app.core.logger import logger
import json

redis = from_url(settings.redis_url, decode_responses=True)

async def get_cached_answer(query: str):
    try:
        value = await redis.get(query)
        if value:
            logger.info(f"[Cache] Cache hit for query: {query}")
            return json.loads(value)
        return None
    except Exception as e:
        logger.error(f"[Cache] Error reading from cache: {e}")
        return None

async def set_cached_answer(query: str, value: dict, ttl: int = 3600):
    try:
        # Convert HttpUrl to str recursively before caching
        def serialize(obj):
            if isinstance(obj, dict):
                return {k: serialize(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [serialize(item) for item in obj]
            elif hasattr(obj, "model_dump"):
                return serialize(obj.model_dump())
            elif hasattr(obj, "__str__"):
                return str(obj)
            return obj

        value = serialize(value)

        await redis.setex(query, ttl, json.dumps(value))
        logger.info(f"[Cache] Cached response for query: {query}")
    except Exception as e:
        logger.error(f"[Cache] Error writing to cache: {e}")


async def rate_limit(key: str):
    try:
        current = await redis.incr(key)
        if current == 1:
            await redis.expire(key, 60)
        return current
    except Exception as e:
        logger.error(f"[Cache] Error in rate limiting: {e}")
        return 0
