from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    llm_provider: str = "auto"
    anthropic_api_key: str = ""
    anthropic_model_fast: str = "claude-sonnet-4-6"
    anthropic_model_strong: str = "claude-opus-4-6"
    groq_api_key: str = ""
    groq_key_file: str = "../groq.key"
    groq_api_base: str = "https://api.groq.com/openai/v1"
    groq_model_fast: str = "llama-3.3-70b-versatile"
    groq_model_strong: str = "llama-3.3-70b-versatile"
    gamma_api_key: str = ""
    gamma_theme_id: str = ""
    gamma_image_model: str = "flux-1-quick"
    gamma_image_style: str = "professional, clean, modern business"
    gamma_prompt_file: str = "app/prompts/gamma_prompt.txt"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()
