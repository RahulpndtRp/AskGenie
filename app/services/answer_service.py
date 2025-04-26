from fastapi import Request
from app.models.schemas import AnswerRequest, AnswerResponse, Source
from app.services.search_selector import search_selector
from app.services.scraper import scrape_documents
from app.services.rag import chunk_and_embed, similarity_search
from app.services.llm import llm_service # generate_answer_text, generate_followup_questions, rephrase_input
from app.cache import get_cached_answer, set_cached_answer
from app.services.utils import rate_limit_check
from app.core.logger import logger

async def generate_answer(endpoint_request: AnswerRequest, request: Request) -> AnswerResponse:
    """
    Orchestrator function to handle the complete answer generation pipeline.
    """
    client_ip = request.client.host

    try:
        if not await rate_limit_check(client_ip):
            logger.warning(f"[Answer Service] Rate limit exceeded for IP: {client_ip}")
            return AnswerResponse(answer="Rate limit exceeded. Please try again later.")

        logger.info(f"[Answer Service] Received request from {client_ip}: {endpoint_request.message}")

        # Check if answer exists in cache
        cached = await get_cached_answer(endpoint_request.message)
        if cached:
            logger.info(f"[Answer Service] Found cached answer for query.")
            return AnswerResponse(**cached)

        # Rephrase the query
        rephrased = await llm_service.rephrase_input(endpoint_request.message)

        # Search documents based on rephrased query
        docs = await search_selector(rephrased, count=endpoint_request.number_of_pages_to_scan)
        scraped_texts, metadatas = await scrape_documents(docs)

        if not scraped_texts:
            logger.error(f"[Answer Service] No documents scraped for query: {rephrased}")
            return AnswerResponse(answer="No relevant sources found.")

        # Chunk and Embed
        store = chunk_and_embed(scraped_texts, metadatas)
        related_docs = similarity_search(store, rephrased, k=endpoint_request.number_of_similarity_results)

        context = "\n\n".join([doc["text"] for doc in related_docs])
        sources = [Source(title=doc.get("title", ""), link=doc.get("link", "")) for doc in related_docs if "link" in doc]

        # Generate the final answer
        answer_content, tool_outputs = await llm_service.generate_answer_text(context, rephrased)

        # Optionally generate follow-up questions
        followups = []
        if endpoint_request.return_follow_up_questions:
            followups = await llm_service.generate_followup_questions(rephrased)  
 
        response = AnswerResponse(
            answer=answer_content,
            sources=sources if endpoint_request.return_sources else None,
            follow_up_questions=followups if endpoint_request.return_follow_up_questions else None,
            tool_outputs=tool_outputs or [],   # ✅ Always pass list even if None
        )

        # Save to cache
        await set_cached_answer(endpoint_request.message, response.dict())

        return response

    except Exception as e:
        logger.error(f"[Answer Service] Unexpected error: {e}")
        return AnswerResponse(answer="An internal error occurred. Please try again later.")
