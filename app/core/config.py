# app/core/config.py

from enum import Enum
from typing import Optional, Dict
from pydantic import Field, HttpUrl
from pydantic_settings import SettingsConfigDict, BaseSettings
from app.core.model_mappings import ModelMappings
import logging

logger = logging.getLogger(__name__)


class LLMProvider(str, Enum):
    """Supported LLM providers."""
    openai = "openai"
    groq = "groq"
    mistral = "mistral"
    cohere = "cohere"
    ollama = "ollama"


class Settings(BaseSettings):
    """Application configuration settings with provider-based model resolution."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="allow"  # ✅ This allows unused env vars like search_provider, redis, etc.
)
    # --- Provider Selection ---
    llm_provider: LLMProvider = Field(default=LLMProvider.openai, env="LLM_PROVIDER")
    embedding_provider: LLMProvider = Field(default=LLMProvider.openai, env="EMBEDDING_PROVIDER")

    # --- API Keys ---
    openai_api_key: str = Field(default="", env="OPENAI_API_KEY")
    groq_api_key: str = Field(default="", env="GROQ_API_KEY")
    mistral_api_key: str = Field(default="", env="MISTRAL_API_KEY")
    cohere_api_key: str = Field(default="", env="COHERE_API_KEY")
    serper_api_key: str = Field(default="", env="SERPER_API_KEY")
    brave_search_api_key: str = Field(default="", env="BRAVE_SEARCH_API_KEY")

    search_provider: str = Field(default="", env="SEARCH_PROVIDER")
    


    # --- Ollama Settings ---
    ollama_base_url: HttpUrl = Field(default="http://localhost:11434", env="OLLAMA_BASE_URL")
    ollama_model: str = Field(default="llama3", env="OLLAMA_MODEL")

    # --- Resolved Model Names ---
    answer_model: Optional[str] = None
    rephrase_model: Optional[str] = None
    followup_model: Optional[str] = None
    embedding_model: Optional[str] = None


    # --- Redis Settings ---
    redis_url: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    redis_host: str = Field(default="localhost", env="REDIS_HOST")
    redis_port: int = Field(default=6379, env="REDIS_PORT")
    redis_password: str = Field(default="", env="REDIS_PASSWORD")
    redis_use_upstash: bool = Field(default=False, env="REDIS_USE_UPSTASH")

    # --- Rate Limiting Settings ---
    requests_per_minute: int = Field(default=30, env="REQUESTS_PER_MINUTE")

    # --- Cache Settings ---
    cache_ttl_seconds: int = Field(default=3600, env="CACHE_TTL_SECONDS")

    # --- Other Optional Settings ---
    use_function_calling: bool = Field(default=True, env="USE_FUNCTION_CALLING")
    use_semantic_cache: bool = Field(default=False, env="USE_SEMANTIC_CACHE")


    def load_model_configs(self) -> None:
        """Load appropriate model names based on selected providers."""
        llm = self.llm_provider.value
        embedding = self.embedding_provider.value

        llm_models: Dict[str, str] = ModelMappings.llm_models().get(llm, {})
        embedding_model: Optional[str] = ModelMappings.embedding_models().get(embedding)

        if not llm_models:
            raise ValueError(f"[Config] Unsupported LLM provider: {llm}")
        if not embedding_model:
            raise ValueError(f"[Config] Unsupported embedding provider: {embedding}")

        self.rephrase_model = llm_models["rephrase_model"]
        self.answer_model = llm_models["answer_model"]
        self.followup_model = llm_models["followup_model"]
        self.embedding_model = embedding_model

        logger.info(f"[Config] LLM Provider: {llm}")
        logger.info(f"[Config] Embedding Provider: {embedding}")
        logger.info("[Config] Loaded Models:")
        logger.info(f"  - rephrase_model: {self.rephrase_model}")
        logger.info(f"  - answer_model: {self.answer_model}")
        logger.info(f"  - followup_model: {self.followup_model}")
        logger.info(f"  - embedding_model: {self.embedding_model}")


# Instantiate and initialize
settings = Settings()
settings.load_model_configs()