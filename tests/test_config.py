from app.bootstrap import build_service_context
from app.config import Settings


def test_settings_parse_env_values() -> None:
    settings = Settings(
        APP_NAME="custom-app",
        APP_VERSION="2.0.0",
        APP_ENV="test",
        APP_DEBUG=False,
        API_HOST="127.0.0.1",
        API_PORT=9000,
        LOG_LEVEL="DEBUG",
        MOCK_MODE=True,
        PROVIDER_TYPE="claude",
        ANTHROPIC_API_KEY="anthropic-secret-key",
        CLAUDE_MODEL="claude-3-5-sonnet-latest",
        VECTORSTORE_BACKEND="chroma",
        DEFAULT_COLLECTION_NAME="integration-tests",
        ENABLE_CORS=True,
        CORS_ORIGINS="http://localhost:3000,http://localhost:5173",
    )

    assert settings.app_name == "custom-app"
    assert settings.app_version == "2.0.0"
    assert settings.app_env == "test"
    assert settings.mock_mode is True
    assert settings.provider_config() == {
        "api_key": "anthropic-secret-key",
        "model": "claude-3-5-sonnet-latest",
    }
    assert settings.cors_origins == ["http://localhost:3000", "http://localhost:5173"]


def test_settings_mask_debug_config() -> None:
    settings = Settings(
        OPENAI_API_KEY="abcd1234wxyz",
        GEMINI_API_KEY="gemini-secret",
        ANTHROPIC_API_KEY="anthropic-secret",
    )

    debug_payload = settings.masked_debug_config()

    assert debug_payload["openai_api_key"] == "abcd****wxyz"
    assert debug_payload["gemini_api_key"] == "gemi*****cret"
    assert debug_payload["anthropic_api_key"] == "anth********cret"


def test_build_service_context_wires_operational_fields() -> None:
    settings = Settings(
        APP_NAME="template-service",
        APP_VERSION="1.2.3",
        APP_DEBUG=True,
        MOCK_MODE=False,
        PROVIDER_TYPE="openai",
        OPENAI_API_KEY="abcd1234wxyz",
        OPENAI_MODEL="text-embedding-3-small",
        VECTORSTORE_BACKEND="chroma",
        DEFAULT_COLLECTION_NAME="documents",
        ENABLE_CORS=True,
    )

    context = build_service_context(settings)

    assert context.service_name == "template-service"
    assert context.service_version == "1.2.3"
    assert context.provider == "openai"
    assert context.available_providers == ("openai", "gemini", "claude")
    assert context.vectorstore == "chroma"
    assert context.available_vectorstores == ("chroma",)
    assert context.masked_secrets["openai_api_key"] == "abcd****wxyz"
    assert context.provider_status_resolver is not None
    assert context.vectorstore_status_resolver is not None
    assert context.provider_diagnostics_resolver is not None
    assert context.vectorstore_diagnostics_resolver is not None
    assert context.benchmarks_resolver is not None
