from openai import AsyncOpenAI
from typing import List, AsyncGenerator
from app.core.config import settings
from app.core.logger import logger

def _configure_client() -> AsyncOpenAI:
    """
    Configure OpenAI or Groq client based on settings.
    """
    if settings.llm_provider.lower() == "groq":
        logger.info("[LLM] Using Groq API client.")
        return AsyncOpenAI(
            api_key=settings.groq_api_key,
            base_url="https://api.groq.com/openai/v1",
        )
    else:
        logger.info("[LLM] Using OpenAI API client.")
        return AsyncOpenAI(
            api_key=settings.openai_api_key,
            base_url="https://api.openai.com/v1",
        )

async def stream_chat_completion(
    messages: List[dict],
    model: str,
) -> AsyncGenerator[str, None]:
    """
    Stream ChatCompletion response.
    """
    client = _configure_client()
    try:
        logger.info(f"[LLM] Streaming chat completion with model: {model}")
        response = await client.chat.completions.create(
            model=model,
            messages=messages,
            stream=True,
        )
        async for chunk in response:
            delta = chunk.choices[0].delta.content
            if delta:
                yield delta
    except Exception as e:
        logger.error(f"[LLM] Error during streaming chat completion: {e}")
        raise

async def chat_completion(
    messages: List[dict],
    model: str,
) -> str:
    """
    Get full ChatCompletion response.
    """
    client = _configure_client()
    try:
        logger.info(f"[LLM] Requesting chat completion with model: {model}")
        response = await client.chat.completions.create(
            model=model,
            messages=messages,
            stream=False,
        )
        content = response.choices[0].message.content
        logger.info(f"[LLM] Chat completion successful.")
        return content
    except Exception as e:
        logger.error(f"[LLM] Error during chat completion: {e}")
        raise


async def rephrase_input(text: str) -> str:
    """
    Rephrase user input for better search.
    """
    try:
        logger.info(f"[Rephrase] Starting rephrasing for input: {text[:50]}...")
        rephrased = await chat_completion(
            messages=[
                {"role": "system", "content": "You are an expert at rephrasing search queries."},
                {"role": "user", "content": text},
            ],
            model=settings.answer_model
        )
        logger.info("[Rephrase] Successfully rephrased input.")
        return rephrased
    except Exception as e:
        logger.error(f"[Rephrase] Error occurred during rephrasing: {e}")
        raise

async def generate_answer_text(context: str, rephrased: str) -> str:
    """
    Generate the final answer from context.
    """
    try:
        user_prompt = f"Context:\n{context}\n\nQuestion:\n{rephrased}"
        answer = await chat_completion(
            messages=[
                {"role": "system", "content": "Answer based only on provided context."},
                {"role": "user", "content": user_prompt},
            ],
            model=settings.answer_model
        )
        return answer
    except Exception as e:
        logger.error(f"[LLM] Error during answer generation: {e}")
        raise

async def generate_followup_questions(rephrased: str) -> List[str]:
    """
    Generate follow-up questions.
    """
    try:
        followup_response = await chat_completion(
            messages=[
                {"role": "system", "content": "Suggest 3 follow-up questions based on the user's question."},
                {"role": "user", "content": rephrased},
            ],
            model=settings.followup_model
        )
        return [q.strip() for q in followup_response.split("\n") if q.strip()]
    except Exception as e:
        logger.error(f"[LLM] Error during follow-up generation: {e}")
        raise