"""
Configuration settings for the DealerFlow Lead Generator
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # LLM Configuration
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.1:8b"

    huggingface_api_token: Optional[str] = None
    huggingface_model: str = "mistralai/Mistral-7B-Instruct-v0.2"

    # Choose LLM provider: "ollama" or "huggingface"
    llm_provider: str = "ollama"

    # Search API Configuration
    tavily_api_key: Optional[str] = None
    serper_api_key: Optional[str] = None
    google_api_key: Optional[str] = None
    google_cse_id: Optional[str] = None

    # Search provider: "tavily", "serper", "google", or "duckduckgo"
    search_provider: str = "duckduckgo"  # Default to free option

    # Prompt Tracing
    langfuse_public_key: Optional[str] = None
    langfuse_secret_key: Optional[str] = None
    langfuse_host: str = "https://cloud.langfuse.com"

    # Application Settings
    log_level: str = "INFO"
    cache_results: bool = True
    max_companies_to_analyze: int = 50  # Increased to ensure we have enough after filtering
    top_n_results: int = 10

    # LLM Parameters
    llm_temperature: float = 0.0  # Deterministic for repeatability
    llm_max_tokens: int = 2048
    llm_timeout: int = 120

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
settings = Settings()
