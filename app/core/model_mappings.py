# app/core/model_mapping.py

from typing import Dict


class ModelMappings:
    """Central registry for supported LLM and embedding model mappings."""

    @staticmethod
    def llm_models() -> Dict[str, Dict[str, str]]:
        """Return supported LLM models per provider."""
        return {
            "openai": {
                "rephrase_model": "gpt-4o-mini",
                "answer_model": "gpt-4o-mini",
                "followup_model": "gpt-4o-mini",
            },
            "groq": {
                "rephrase_model": "llama-guard-3-8b",
                "answer_model": "llama-3.3-70b-versatile",
                "followup_model": "llama-3.3-70b-versatile",
            },
            "mistral": {
                "rephrase_model": "mistral-large-latest",
                "answer_model": "mistral-large-latest",
                "followup_model": "mistral-large-latest",
            },
            "cohere": {
                "rephrase_model": "command-r",
                "answer_model": "command-r",
                "followup_model": "command-r",
            },
            "ollama": {
                "rephrase_model": "llama3",
                "answer_model": "llama3",
                "followup_model": "llama3",
            },
        }

    @staticmethod
    def embedding_models() -> Dict[str, str]:
        """Return supported embedding models per provider."""
        return {
            "openai": "text-embedding-ada-002",
            "groq": "text-embedding-ada-002",
            "mistral": "mistral-embed",
            "cohere": "embed-english-v3",
            "ollama": "bge-large",
        }
