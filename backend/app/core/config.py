import os
from functools import lru_cache

from dotenv import load_dotenv

load_dotenv()


class Settings:
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./cpaos_dev.db")
    supabase_url: str | None = os.getenv("SUPABASE_URL")
    supabase_service_key: str | None = os.getenv("SUPABASE_SERVICE_KEY")
    supabase_storage_bucket: str = os.getenv("SUPABASE_STORAGE_BUCKET", "cpaos-documents")
    anthropic_api_key: str | None = os.getenv("ANTHROPIC_API_KEY")
    n8n_webhook_url: str | None = os.getenv("N8N_WEBHOOK_URL")
    twilio_account_sid: str | None = os.getenv("TWILIO_ACCOUNT_SID")
    twilio_auth_token: str | None = os.getenv("TWILIO_AUTH_TOKEN")
    twilio_from_number: str | None = os.getenv("TWILIO_FROM_NUMBER")
    docusign_integration_key: str | None = os.getenv("DOCUSIGN_INTEGRATION_KEY")
    docusign_account_id: str | None = os.getenv("DOCUSIGN_ACCOUNT_ID")
    docusign_private_key: str | None = os.getenv("DOCUSIGN_PRIVATE_KEY")
    docusign_user_id: str | None = os.getenv("DOCUSIGN_USER_ID")
    docusign_env: str = os.getenv("DOCUSIGN_ENV", "demo")
    vapi_webhook_secret: str | None = os.getenv("VAPI_WEBHOOK_SECRET")
    slack_webhook_url: str | None = os.getenv("SLACK_WEBHOOK_URL")
    resend_api_key: str | None = os.getenv("RESEND_API_KEY")
    from_email: str | None = os.getenv("FROM_EMAIL")
    secret_key: str = os.getenv("SECRET_KEY", "dev-change-me")
    frontend_url: str = os.getenv("FRONTEND_URL", "http://localhost:5173")
    port: int = int(os.getenv("PORT", "8001"))


@lru_cache
def get_settings() -> Settings:
    return Settings()
