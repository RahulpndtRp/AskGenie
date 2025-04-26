# app/services/llm.py

from openai import AsyncOpenAI
from typing import List, Dict, AsyncGenerator, Optional, Tuple
from app.core.config import settings
from app.core.logger import logger
from app.services.functions import FUNCTIONS, handle_function_call

class LLMService:
    def __init__(self):
        self.client = self._configure_client()

    def _configure_client(self) -> AsyncOpenAI:
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
        self,
        messages: List[dict],
        model: str,
    ) -> AsyncGenerator[str, None]:
        """
        Stream ChatCompletion response.
        """
        try:
            logger.info(f"[LLM] Streaming chat completion with model: {model}")
            response = await self.client.chat.completions.create(
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
        self,
        messages: List[dict],
        model: str,
        enable_function_calling: bool = False,
    ) -> Tuple[str, Optional[List[dict]]]:
        """
        Get full ChatCompletion response.
        Handles multiple function calls with summarization.
        Returns: (final_answer, tool_outputs_list)
        """
        try:
            use_functions = settings.use_function_calling and enable_function_calling
            logger.info(f"[LLM] Requesting chat completion with model: {model} (function calling: {use_functions})")

            kwargs = {
                "model": model,
                "messages": messages,
                "stream": False,
            }

            if use_functions:
                kwargs.update({
                    "tools": [{"type": "function", "function": f} for f in FUNCTIONS],
                    "tool_choice": "auto",
                })

            response = await self.client.chat.completions.create(**kwargs)
            choice = response.choices[0]

            if hasattr(choice.message, "tool_calls") and choice.message.tool_calls:
                logger.info(f"[LLM] ✅ {len(choice.message.tool_calls)} function call(s) detected.")

                tool_outputs_summary = []
                tool_outputs_json = []

                import json

                for tool_call in choice.message.tool_calls:
                    function_name = tool_call.function.name
                    function_args_json = tool_call.function.arguments
                    function_args = json.loads(function_args_json)

                    function_response = await handle_function_call(function_name, function_args)
                    logger.info(f"[LLM] 🔥 Function {function_name} executed successfully.")

                    tool_outputs_summary.append(f"- {function_response}")
                    tool_outputs_json.append({
                        "function_name": function_name,
                        "arguments": function_args,
                        "response": function_response,
                    })

                summary_prompt = [
                    {
                        "role": "system",
                        "content": "You are an intelligent assistant. Given the following tool outputs, summarize them into a clean, readable paragraph."
                    },
                    {
                        "role": "user",
                        "content": "\n".join(tool_outputs_summary),
                    },
                ]

                logger.info("[LLM] 📥 Sending summarized function outputs to model...")
                second_response = await self.client.chat.completions.create(
                    model=model,
                    messages=summary_prompt,
                    stream=False,
                )

                final_content = second_response.choices[0].message.content
                logger.info("[LLM] 🎯 Final summarized answer generated.")

                return final_content, tool_outputs_json

            else:
                logger.info("[LLM] Chat completion successful without function calling.")
                return choice.message.content, None

        except Exception as e:
            logger.error(f"[LLM] Error during chat completion: {e}")
            raise

    async def generate_answer_text(self, context: str, user_question: str) -> str:
        """
        Generate final answer text based on scraped context and user question.
        """
        try:
            logger.info("[LLM] Generating answer text...")
            prompt = [
                {"role": "system", "content": "You are an intelligent assistant who uses the provided context to answer user questions."},
                {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {user_question}"},
            ]
            return await self.chat_completion(
                messages=prompt,
                model=settings.answer_model,
                enable_function_calling=settings.use_function_calling,
            )
        except Exception as e:
            logger.error(f"[LLM] Error generating answer text: {e}")
            return "An error occurred while generating the answer."

    async def rephrase_input(self, user_input: str) -> str:
        """
        Rephrase user's input to improve search relevance.
        """
        try:
            logger.info(f"[Rephrase] Starting rephrasing for input: {user_input}...")
            prompt = [
                {"role": "system", "content": "You are an assistant skilled at rephrasing queries for better search results."},
                {"role": "user", "content": f"Rephrase this query to make it more precise for search engines: {user_input}"},
            ]
            rephrased_input, _ =  await self.chat_completion(messages=prompt, model=settings.rephrase_model)
            return rephrased_input
        except Exception as e:
            logger.error(f"[LLM] Error during rephrasing: {e}")
            return user_input

    async def generate_followup_questions(self, user_question: str) -> List[str]:
        """
        Generate follow-up questions related to the user's query.
        """
        try:
            logger.info("[LLM] Generating follow-up questions...")
            prompt = [
                {"role": "system", "content": "Generate 3 short, relevant follow-up questions for the given query."},
                {"role": "user", "content": user_question},
            ]
            followup_text, _ = await self.chat_completion(messages=prompt, model=settings.followup_model)
            return [q.strip() for q in followup_text.split('\n') if q.strip()]
        except Exception as e:
            logger.error(f"[LLM] Error generating follow-up questions: {e}")
            return []

# ✅ Instantiate LLMService once
llm_service = LLMService()
