from __future__ import annotations

from collections.abc import Mapping
from functools import lru_cache
from typing import Any

from ai_service_kit.utils import mask_secret
from ai_service_kit.logging import Logger
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Application settings
    app_name: str = Field(default="ai-service-template", alias="APP_NAME")
    app_version: str = Field(default="0.1.0", alias="APP_VERSION")
    app_env: str = Field(default="development", alias="APP_ENV")
    app_debug: bool = Field(default=True, alias="APP_DEBUG")
    api_host: str = Field(default="0.0.0.0", alias="API_HOST")
    api_port: int = Field(default=8000, alias="API_PORT")
    mock_mode: bool = Field(default=False, alias="MOCK_MODE")
    
    # Enhanced logging configuration
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    file_log_level: str = Field(default="DEBUG", alias="FILE_LOG_LEVEL")
    error_file_level: str = Field(default="ERROR", alias="ERROR_FILE_LEVEL")
    log_structured: bool = Field(default=True, alias="LOG_STRUCTURED")
    log_console: bool = Field(default=True, alias="LOG_CONSOLE")
    log_dir: str = Field(default="./logs", alias="LOG_DIR")
    log_max_file_size: int = Field(default=10485760, alias="LOG_MAX_FILE_SIZE")
    log_backup_count: int = Field(default=5, alias="LOG_BACKUP_COUNT")
    cloud_logging_providers: list[str] = Field(default_factory=list, alias="CLOUD_LOGGING_PROVIDERS")
    
    # Cloud logging - AWS
    aws_logging_enabled: bool = Field(default=False, alias="AWS_LOGGING_ENABLED")
    aws_logging_level: str = Field(default="ERROR", alias="AWS_LOGGING_LEVEL")
    aws_log_group: str = Field(default="/ai-service-template/production", alias="AWS_LOG_GROUP")
    aws_region: str = Field(default="us-east-1", alias="AWS_REGION")
    
    # Cloud logging - Datadog
    datadog_logging_enabled: bool = Field(default=False, alias="DATADOG_LOGGING_ENABLED")
    datadog_logging_level: str = Field(default="INFO", alias="DATADOG_LOGGING_LEVEL")
    datadog_api_key: str | None = Field(default=None, alias="DATADOG_API_KEY")
    
    # Provider configuration
    provider_type: str = Field(default="openai", alias="PROVIDER_TYPE")
    openai_api_key: str | None = Field(default=None, alias="OPENAI_API_KEY")
    openai_model: str = Field(default="text-embedding-3-small", alias="OPENAI_MODEL")
    gemini_api_key: str | None = Field(default=None, alias="GEMINI_API_KEY")
    gemini_model: str = Field(default="models/embedding-001", alias="GEMINI_MODEL")
    anthropic_api_key: str | None = Field(default=None, alias="ANTHROPIC_API_KEY")
    claude_model: str = Field(default="claude-3-5-haiku-latest", alias="CLAUDE_MODEL")
    
    # Vector store configuration
    vectorstore_backend: str = Field(default="chroma", alias="VECTORSTORE_BACKEND")
    default_collection_name: str = Field(default="default", alias="DEFAULT_COLLECTION_NAME")
    
    # CORS configuration
    enable_cors: bool = Field(default=True, alias="ENABLE_CORS")
    cors_origins: list[str] = Field(
        default_factory=lambda: ["http://localhost:3000", "http://localhost:5173"],
        alias="CORS_ORIGINS",
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
        populate_by_name=True,
    )

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: str | list[str] | None) -> list[str]:
        if value is None:
            return []
        if isinstance(value, list):
            return [item.strip() for item in value if item.strip()]
        return [item.strip() for item in value.split(",") if item.strip()]
    
    @field_validator("cloud_logging_providers", mode="before")
    @classmethod
    def parse_cloud_providers(cls, value: str | list[str] | None) -> list[str]:
        if value is None or value == "":
            return []
        if isinstance(value, list):
            return [item.strip().lower() for item in value if item.strip()]
        return [item.strip().lower() for item in value.split(",") if item.strip()]

    def provider_config(self) -> dict[str, Any]:
        provider_name = self.provider_type.strip().lower()
        try:
            if provider_name == "openai":
                return {
                    "api_key": self.openai_api_key,
                    "model": self.openai_model,
                }
            if provider_name == "gemini":
                return {
                    "api_key": self.gemini_api_key,
                    "model": self.gemini_model,
                }
            if provider_name == "claude":
                return {
                    "api_key": self.anthropic_api_key,
                    "model": self.claude_model,
                }
            Logger.warning(f"Unknown provider type: {provider_name}")
            return {}
        except Exception as e:
            Logger.error(f"Failed to build provider config for {provider_name}: {e}", exc_info=True)
            return {}

    def selected_provider_model(self) -> str | None:
        return self.provider_config().get("model")

    def selected_provider_api_key(self) -> str | None:
        return self.provider_config().get("api_key")

    def operational_settings(self) -> dict[str, Any]:
        return {
            "app_env": self.app_env,
            "app_debug": self.app_debug,
            "api_host": self.api_host,
            "api_port": self.api_port,
            "log_level": self.log_level,
            "mock_mode": self.mock_mode,
            "provider_type": self.provider_type,
            "provider_model": self.selected_provider_model(),
            "vectorstore_backend": self.vectorstore_backend,
            "default_collection_name": self.default_collection_name,
            "enable_cors": self.enable_cors,
            "cors_origins": list(self.cors_origins),
        }

    def masked_secrets(self) -> dict[str, str | None]:
        return {
            "openai_api_key": mask_secret(self.openai_api_key),
            "gemini_api_key": mask_secret(self.gemini_api_key),
            "anthropic_api_key": mask_secret(self.anthropic_api_key),
            "datadog_api_key": mask_secret(self.datadog_api_key),
        }

    def masked_debug_config(self) -> Mapping[str, Any]:
        return {
            "app_name": self.app_name,
            "app_version": self.app_version,
            "app_env": self.app_env,
            "app_debug": self.app_debug,
            "api_host": self.api_host,
            "api_port": self.api_port,
            "log_level": self.log_level,
            "file_log_level": self.file_log_level,
            "error_file_level": self.error_file_level,
            "log_structured": self.log_structured,
            "log_console": self.log_console,
            "log_dir": self.log_dir,
            "cloud_logging_providers": self.cloud_logging_providers,
            "mock_mode": self.mock_mode,
            "provider_type": self.provider_type,
            "openai_api_key": self.masked_secrets()["openai_api_key"],
            "openai_model": self.openai_model,
            "gemini_api_key": self.masked_secrets()["gemini_api_key"],
            "gemini_model": self.gemini_model,
            "anthropic_api_key": self.masked_secrets()["anthropic_api_key"],
            "claude_model": self.claude_model,
            "datadog_api_key": self.masked_secrets()["datadog_api_key"],
            "vectorstore_backend": self.vectorstore_backend,
            "default_collection_name": self.default_collection_name,
            "enable_cors": self.enable_cors,
            "cors_origins": self.cors_origins,
        }


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    try:
        settings = Settings()
        # Note: Logger may not be configured yet during initial setup
        return settings
    except Exception as e:
        # Use print since Logger might not be configured yet
        print(f"Failed to load settings: {e}")
        raise
