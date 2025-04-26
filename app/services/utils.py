from app.cache import rate_limit
from app.core.logger import logger
from app.core.config import settings

async def rate_limit_check(client_ip: str) -> bool:
    if await rate_limit(f"rate:{client_ip}") > settings.requests_per_minute:
        logger.warning(f"[Answer Service] Rate limit exceeded for IP: {client_ip}")
        return False
    return True