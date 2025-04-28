# app/core/config.py

from pydantic import Field, HttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

    # --- LLM Provider ---
    llm_provider: str = Field(default="openai", env="LLM_PROVIDER")  # openai, groq, ollama

    # --- Search Provider ---
    search_provider: str = Field(default="serper", env="SEARCH_PROVIDER")  # serper or brave

    # --- API Keys ---
    openai_api_key: str = Field(default="", env="OPENAI_API_KEY")
    groq_api_key: str = Field(default="", env="GROQ_API_KEY")
    mistral_api_key: str = Field(default="", env="MISTRAL_API_KEY")
    serper_api_key: str = Field(default="", env="SERPER_API_KEY")
    brave_search_api_key: str = Field(default="", env="BRAVE_SEARCH_API_KEY")
    

    # --- Ollama Settings ---
    ollama_base_url: HttpUrl = Field(default="http://localhost:11434", env="OLLAMA_BASE_URL")
    ollama_model: str = Field(default="llama3", env="OLLAMA_MODEL")

    # --- Model Names for Different Steps ---
    rephrase_model: str = Field(default="gpt-3.5-turbo", env="REPHRASE_MODEL")
    answer_model: str = Field(default="gpt-3.5-turbo", env="ANSWER_MODEL")
    followup_model: str = Field(default="gpt-3.5-turbo", env="FOLLOWUP_MODEL")
    embedding_model: str = Field(default="text-embedding-ada-002", env="EMBEDDING_MODEL")

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

# Global Settings Singleton
settings = Settings()
