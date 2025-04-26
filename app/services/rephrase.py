from app.services.llm import chat_completion
from app.core.config import settings
from app.core.logger import logger

async def rephrase_input(input_text: str) -> str:
    """
    Rephrase input_text using configured LLM.
    Logs request and response, handles LLM errors.
    """
    try:
        logger.info(f"[Rephrase] Starting rephrasing for input: {input_text[:50]}...")

        response = await chat_completion(
            messages=[
                {
                    "role": "system",
                    "content": "You are a rephraser and always rephrase the input. ONLY RETURN THE REPHRASED VERSION OF THE INPUT."
                },
                {"role": "user", "content": input_text},
            ],
            model=settings.rephrase_model,
        )

        logger.info(f"[Rephrase] Successfully rephrased input.")
        return response

    except Exception as e:
        logger.error(f"[Rephrase] Error occurred during rephrasing: {e}")
        raise
