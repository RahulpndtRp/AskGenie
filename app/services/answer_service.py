from fastapi import Request
from app.models.schemas import AnswerRequest, AnswerResponse, Source
from fastapi.responses import StreamingResponse
from app.services.search_selector import search_selector
from app.services.scraper import scrape_documents
from app.services.rag import embedding_service
from app.services.llm import llm_service
from app.cache import get_cached_answer, set_cached_answer
from app.services.utils import rate_limit_check
from app.core.logger import logger
import traceback
from app.models.schemas import AnswerRequest, Source
from app.services.search_selector import search_selector
from app.services.scraper import scrape_documents
from app.services.rag import embedding_service
from app.services.llm import llm_service
from app.cache import get_cached_answer, set_cached_answer
from app.services.utils import rate_limit_check
from app.core.logger import logger
from app.core.config import settings
import traceback
import json
from typing import AsyncGenerator



async def generate_answer(endpoint_request: AnswerRequest, request: Request) -> AnswerResponse:
    """
    Orchestrator function to handle the complete answer generation pipeline.
    """
    client_ip = request.client.host

    logger.info(f"[Answer Service] Received request from {client_ip}")
    logger.debug(f"Request payload: {endpoint_request.model_dump()}")

    try:
        logger.debug(f"Type of number_of_pages_to_scan: {type(endpoint_request.number_of_pages_to_scan)}")
        logger.debug(f"Type of number_of_similarity_results: {type(endpoint_request.number_of_similarity_results)}")

        if not await rate_limit_check(client_ip):
            logger.warning(f"[Answer Service] Rate limit exceeded for IP: {client_ip}")
            return AnswerResponse(answer="Rate limit exceeded. Please try again later.")

        # Cache check
        cached = await get_cached_answer(endpoint_request.message)
        if cached:
            logger.info(f"[Answer Service] Found cached answer for query: {endpoint_request.message}")
            return AnswerResponse(**cached)

        # Rephrase
        logger.debug("[Answer Service] Rephrasing query...")
        rephrased = await llm_service.rephrase_input(endpoint_request.message)
        logger.debug(f"[Answer Service] Rephrased query: {rephrased}")

        # Search and scrape
        logger.debug("[Answer Service] Searching documents...")
        docs = await search_selector(rephrased, count=endpoint_request.number_of_pages_to_scan)
        logger.debug(f"[Answer Service] Search returned {len(docs)} documents.")

        scraped_texts, metadatas = await scrape_documents(docs)
        logger.debug(f"[Answer Service] Scraped {len(scraped_texts)} documents.")

        if not scraped_texts:
            logger.error(f"[Answer Service] No documents scraped for query: {rephrased}")
            return AnswerResponse(answer="No relevant sources found.")

        # Embed
        logger.debug("[Answer Service] Chunking and embedding scraped content...")
        store = embedding_service.chunk_and_embed(scraped_texts, metadatas)
        related_docs = embedding_service.similarity_search(
            store, rephrased, k=endpoint_request.number_of_similarity_results
        )

        context = "\n\n".join([doc["text"] for doc in related_docs])
        sources = [
            Source(title=doc.get("title", ""), link=doc.get("link", ""))
            for doc in related_docs if "link" in doc
        ]

        # Generate answer
        logger.debug("[Answer Service] Generating final answer using LLM...")
        answer_content, tool_outputs = await llm_service.generate_answer_text(context, rephrased)

        # Follow-ups
        followups = []
        if endpoint_request.return_follow_up_questions:
            logger.debug("[Answer Service] Generating follow-up questions...")
            followups = await llm_service.generate_followup_questions(rephrased)

        # Final response
        response = AnswerResponse(
            answer=answer_content,
            sources=sources if endpoint_request.return_sources else None,
            follow_up_questions=followups if endpoint_request.return_follow_up_questions else None,
            tool_outputs=tool_outputs or [],
        )

        # Cache response
        await set_cached_answer(endpoint_request.message, response.model_dump())

        logger.info(f"[Answer Service] Successfully generated answer for: {endpoint_request.message}")
        return response

    except Exception as e:
        tb_str = traceback.format_exc()
        logger.error(f"[Answer Service] ❌ Exception occurred: {e}\nTraceback:\n{tb_str}")
        return AnswerResponse(answer="An internal error occurred. Please try again later.")



async def stream_generate_answer(endpoint_request: AnswerRequest, request: Request) -> StreamingResponse:
    client_ip = request.client.host
    logger.info(f"[Answer Stream] Received request from {client_ip}")
    logger.debug(f"Request payload: {endpoint_request.model_dump()}")

    async def streamer() -> AsyncGenerator[str, None]:
        try:
            # Rate limit
            if not await rate_limit_check(client_ip):
                yield "Rate limit exceeded. Please try again later."
                return

            # Cache check
            cached = await get_cached_answer(endpoint_request.message)
            if cached:
                logger.info("[Answer Stream] Cache hit.")
                yield cached.get("answer", "")
                return

            # 1️⃣ Rephrase
            yield "###ACTIVITY### 🔄 Rephrasing query...\n"
            rephrased = await llm_service.rephrase_input(endpoint_request.message)

            # 2️⃣ Search
            yield "###ACTIVITY### 🔍 Searching documents...\n"
            docs = await search_selector(rephrased, count=endpoint_request.number_of_pages_to_scan)

            # 3️⃣ Scrape
            yield "###ACTIVITY### 📄 Scraping content...\n"
            scraped_texts, metadatas = await scrape_documents(docs)
            if not scraped_texts:
                yield "No relevant documents found."
                return

            # 4️⃣ Embed
            yield "###ACTIVITY### 📦 Chunking & embedding...\n"
            store = embedding_service.chunk_and_embed(scraped_texts, metadatas)

            # 5️⃣ Similarity
            yield "###ACTIVITY### 🤝 Matching relevant info...\n"
            related_docs = embedding_service.similarity_search(
                store, rephrased, k=endpoint_request.number_of_similarity_results
            )

            context = "\n\n".join([doc["text"] for doc in related_docs])
            sources = [
                Source(title=doc.get("title", ""), link=doc.get("link", ""))
                for doc in related_docs if "link" in doc
            ]

            # 6️⃣ Generate Answer
            yield "###ACTIVITY### 🧠 Generating answer...\n"
            prompt = [
                {"role": "system", "content": "You are an intelligent assistant who uses the provided context to answer user questions."},
                {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {rephrased}"}
            ]

            async for token in llm_service.stream_chat_completion(messages=prompt, model=settings.answer_model):
                yield token

            # 7️⃣ Tool Execution
            yield "\n###ACTIVITY### 🧰 Running tools if needed...\n"
            _, tool_outputs = await llm_service.chat_completion(
                messages=prompt,
                model=settings.answer_model,
                enable_function_calling=settings.use_function_calling
            )

            if tool_outputs:
                yield "\n###ACTIVITY### 🧾 Tool results ready\n"
                yield "###TOOL_OUTPUT### " + json.dumps(tool_outputs)

        except Exception as e:
            tb = traceback.format_exc()
            logger.error(f"[Answer Stream] ❌ Error: {e}\n{tb}")
            yield "\nAn error occurred while generating the answer."

    return StreamingResponse(streamer(), media_type="text/plain")