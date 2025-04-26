import httpx
from bs4 import BeautifulSoup
import re
from app.core.logger import logger


async def fetch_page_content(url: str, timeout: int = 10) -> str:
    """
    Fetch raw HTML from URL asynchronously with User-Agent header.
    """
    try:
        if not isinstance(url, str):
            logger.warning(f"[Scraper] URL is not string, converting: {url}")
            url = str(url)

        logger.info(f"[Scraper] Fetching page: {url}")
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            return response.text
    except httpx.HTTPStatusError as e:
        logger.error(f"[Scraper] HTTP error while fetching {url}: {e}")
        raise
    except httpx.RequestError as e:
        logger.error(f"[Scraper] Request failed for {url}: {e}")
        raise
    except Exception as e:
        logger.error(f"[Scraper] Unexpected error while fetching {url}: {e}")
        raise

def extract_main_content(html: str) -> str:
    """
    Extract the main textual content from raw HTML.
    Cleans unnecessary tags and logs the process.
    """
    try:
        logger.info(f"[Scraper] Extracting main content from HTML...")
        soup = BeautifulSoup(html, "lxml")
        for tag in soup(["script", "style", "head", "nav", "footer", "iframe", "img"]):
            tag.decompose()
        text = soup.get_text(separator=" ")
        cleaned_text = re.sub(r"\s+", " ", text).strip()
        logger.info(f"[Scraper] Content extraction completed successfully.")
        return cleaned_text
    except Exception as e:
        logger.error(f"[Scraper] Error during HTML content extraction: {e}")
        raise


async def scrape_documents(docs: list) -> tuple[list, list]:
    scraped_texts, metadatas = [], []
    for doc in docs:
        try:
            content = await fetch_page_content(str(doc.link))
            text = extract_main_content(content)
            scraped_texts.append(text)
            metadatas.append({"title": doc.title, "link": str(doc.link)})
        except Exception as e:
            logger.error(f"[Answer Service] Failed to scrape {doc.link}: {e}")
    return scraped_texts, metadatas