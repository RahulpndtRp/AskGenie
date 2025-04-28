from app.services.search import brave_search, serper_search
from app.core.config import settings
from app.core.logger import logger

async def search_selector(query: str, count: int = 4):
    """
    Select search provider dynamically based on settings.
    """
    try:
        provider = settings.search_provider.lower()

        if provider == "serper":
            logger.info(f"[Search Selector] Using Serper search first for query: {query}")
            results = await serper_search(query, count)
            if not results:
                logger.warning(f"[Search Selector] Serper returned no results")
                # results = await brave_search(query, count)

        elif provider == "brave":
            logger.info(f"[Search Selector] Using Brave search first for query: {query}")
            results = await brave_search(query, count)
            if not results:
                logger.warning(f"[Search Selector] Brave returned no results")
                # results = await serper_search(query, count)
        else:
            logger.error(f"[Search Selector] Invalid search engine provider: {provider}")
            return []

        return results

    except Exception as e:
        logger.error(f"[Search Selector] Search failed: {e}")
        return []
