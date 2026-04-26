from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from ai_service_kit.health import (
    BaseHealthCheck,
    CheckResult,
    ComponentKind,
    ComponentStatus,
    HealthStatus,
    NoOpMetricsCollector,
    ProviderDiagnosticsResult,
    ServiceContext,
    VectorStoreDiagnosticsResult,
)
from ai_service_kit.logging import Logger

from .config import Settings

SUPPORTED_PROVIDERS = ("openai", "gemini", "claude")
SUPPORTED_VECTORSTORES = ("chroma",)


@dataclass(slots=True)
class ProviderRuntime:
    name: str
    model: str | None
    configured: bool
    supported: bool
    initialized: bool


@dataclass(slots=True)
class VectorStoreRuntime:
    backend: str
    default_collection_name: str
    configured: bool
    supported: bool
    initialized: bool
    collections_count: int


class ConfigurationHealthCheck(BaseHealthCheck):
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    @property
    def name(self) -> str:
        return "configuration"

    async def run(self) -> CheckResult:
        try:
            Logger.debug("Running configuration health check")
            provider_name = self._settings.provider_type.strip().lower()
            vectorstore_backend = self._settings.vectorstore_backend.strip().lower()
            errors: list[str] = []

            if provider_name not in SUPPORTED_PROVIDERS:
                error_msg = f"Unsupported provider: {provider_name}"
                Logger.warning(error_msg)
                errors.append(error_msg)
            elif not self._settings.selected_provider_api_key():
                error_msg = f"Missing API key for provider: {provider_name}"
                Logger.warning(error_msg)
                errors.append(error_msg)

            if vectorstore_backend not in SUPPORTED_VECTORSTORES:
                error_msg = f"Unsupported vector store backend: {vectorstore_backend}"
                Logger.warning(error_msg)
                errors.append(error_msg)

            if not errors:
                status = HealthStatus.HEALTHY
                summary = "Operational configuration is valid"
                Logger.debug("Configuration health check passed")
            elif any(error.startswith("Unsupported") for error in errors):
                status = HealthStatus.CRITICAL
                summary = "Operational configuration contains unsupported components"
                Logger.error(f"Configuration health check critical: {summary}")
            else:
                status = HealthStatus.DEGRADED
                summary = "Operational configuration is incomplete"
                Logger.warning(f"Configuration health check degraded: {summary}")

            return CheckResult(
                name=self.name,
                status=status,
                summary=summary,
                details={
                    "provider_type": provider_name,
                    "available_providers": list(SUPPORTED_PROVIDERS),
                    "vectorstore_backend": vectorstore_backend,
                    "available_vectorstores": list(SUPPORTED_VECTORSTORES),
                },
                errors=tuple(errors),
            )
        except Exception as e:
            Logger.error(f"Configuration health check failed: {e}", exc_info=True)
            return CheckResult(
                name=self.name,
                status=HealthStatus.CRITICAL,
                summary="Configuration health check failed",
                details={},
                errors=(str(e),),
            )


def _build_provider_runtime(settings: Settings) -> ProviderRuntime:
    try:
        provider_name = settings.provider_type.strip().lower()
        supported = provider_name in SUPPORTED_PROVIDERS
        configured = supported and bool(settings.selected_provider_api_key())
        initialized = configured
        
        Logger.debug(f"Built provider runtime: {provider_name} (configured: {configured}, supported: {supported})")
        
        return ProviderRuntime(
            name=provider_name,
            model=settings.selected_provider_model(),
            configured=configured,
            supported=supported,
            initialized=initialized,
        )
    except Exception as e:
        Logger.error(f"Failed to build provider runtime: {e}", exc_info=True)
        return ProviderRuntime(
            name="unknown",
            model=None,
            configured=False,
            supported=False,
            initialized=False,
        )


def _build_vectorstore_runtime(settings: Settings) -> VectorStoreRuntime:
    try:
        backend = settings.vectorstore_backend.strip().lower()
        supported = backend in SUPPORTED_VECTORSTORES
        configured = supported and bool(settings.default_collection_name)
        initialized = configured
        
        Logger.debug(f"Built vectorstore runtime: {backend} (configured: {configured}, supported: {supported})")
        
        return VectorStoreRuntime(
            backend=backend,
            default_collection_name=settings.default_collection_name,
            configured=configured,
            supported=supported,
            initialized=initialized,
            collections_count=1 if configured else 0,
        )
    except Exception as e:
        Logger.error(f"Failed to build vectorstore runtime: {e}", exc_info=True)
        return VectorStoreRuntime(
            backend="unknown",
            default_collection_name="",
            configured=False,
            supported=False,
            initialized=False,
            collections_count=0,
        )


def _provider_status(provider_runtime: ProviderRuntime) -> ComponentStatus:
    if not provider_runtime.supported:
        status = HealthStatus.CRITICAL
        error = f"Unsupported provider: {provider_runtime.name}"
    elif not provider_runtime.configured:
        status = HealthStatus.DEGRADED
        error = f"Missing credentials for provider: {provider_runtime.name}"
    else:
        status = HealthStatus.HEALTHY
        error = None

    return ComponentStatus(
        name=provider_runtime.name,
        kind=ComponentKind.PROVIDER,
        status=status,
        configured=provider_runtime.configured,
        available=provider_runtime.supported,
        initialized=provider_runtime.initialized,
        details={"model": provider_runtime.model},
        error=error,
    )


def _vectorstore_status(vectorstore_runtime: VectorStoreRuntime) -> ComponentStatus:
    if not vectorstore_runtime.supported:
        status = HealthStatus.CRITICAL
        error = f"Unsupported vector store backend: {vectorstore_runtime.backend}"
    elif not vectorstore_runtime.configured:
        status = HealthStatus.DEGRADED
        error = f"Vector store backend is missing required configuration: {vectorstore_runtime.backend}"
    else:
        status = HealthStatus.HEALTHY
        error = None

    return ComponentStatus(
        name=vectorstore_runtime.backend,
        kind=ComponentKind.VECTORSTORE,
        status=status,
        configured=vectorstore_runtime.configured,
        available=vectorstore_runtime.supported,
        initialized=vectorstore_runtime.initialized,
        details={"default_collection_name": vectorstore_runtime.default_collection_name},
        error=error,
    )


def _provider_diagnostics(provider_runtime: ProviderRuntime) -> ProviderDiagnosticsResult:
    provider_status = _provider_status(provider_runtime)
    return ProviderDiagnosticsResult(
        provider=provider_runtime.name,
        status=provider_status.status,
        configured=provider_runtime.configured,
        available=provider_runtime.supported,
        initialized=provider_runtime.initialized,
        models_available=(provider_runtime.model,) if provider_runtime.model else (),
        error=provider_status.error,
        details={"model": provider_runtime.model},
    )


def _vectorstore_diagnostics(vectorstore_runtime: VectorStoreRuntime) -> VectorStoreDiagnosticsResult:
    vectorstore_status = _vectorstore_status(vectorstore_runtime)
    return VectorStoreDiagnosticsResult(
        backend=vectorstore_runtime.backend,
        status=vectorstore_status.status,
        configured=vectorstore_runtime.configured,
        available=vectorstore_runtime.supported,
        initialized=vectorstore_runtime.initialized,
        collections_count=vectorstore_runtime.collections_count,
        default_collection=vectorstore_runtime.default_collection_name,
        error=vectorstore_status.error,
        details={"default_collection_name": vectorstore_runtime.default_collection_name},
    )


def debug_snapshot(context: ServiceContext) -> dict[str, Any]:
    configuration = context.configuration()
    return {
        "service_name": context.service_name,
        "service_version": context.service_version,
        "configuration": asdict(configuration),
        "metrics_collector": type(context.metrics_collector).__name__,
        "health_checks": [getattr(check, "name", type(check).__name__) for check in context.health_checks],
        "diagnostics_checks": [getattr(check, "name", type(check).__name__) for check in context.diagnostics_checks],
    }


def build_service_context(settings: Settings) -> ServiceContext:
    try:
        Logger.info(f"Building service context for {settings.app_name} v{settings.app_version}")
        
        provider_runtime = _build_provider_runtime(settings)
        vectorstore_runtime = _build_vectorstore_runtime(settings)
        metrics_collector = NoOpMetricsCollector()
        configuration_check = ConfigurationHealthCheck(settings)

        async def provider_status_resolver() -> tuple[ComponentStatus, ...]:
            try:
                result = (_provider_status(provider_runtime),)
                Logger.debug("Provider status resolved successfully")
                return result
            except Exception as e:
                Logger.error(f"Provider status resolution failed: {e}", exc_info=True)
                raise

        async def vectorstore_status_resolver() -> tuple[ComponentStatus, ...]:
            try:
                result = (_vectorstore_status(vectorstore_runtime),)
                Logger.debug("Vectorstore status resolved successfully")
                return result
            except Exception as e:
                Logger.error(f"Vectorstore status resolution failed: {e}", exc_info=True)
                raise

        async def provider_diagnostics_resolver() -> tuple[ProviderDiagnosticsResult, ...]:
            try:
                result = (_provider_diagnostics(provider_runtime),)
                Logger.debug("Provider diagnostics resolved successfully")
                return result
            except Exception as e:
                Logger.error(f"Provider diagnostics resolution failed: {e}", exc_info=True)
                raise

        async def vectorstore_diagnostics_resolver() -> tuple[VectorStoreDiagnosticsResult, ...]:
            try:
                result = (_vectorstore_diagnostics(vectorstore_runtime),)
                Logger.debug("Vectorstore diagnostics resolved successfully")
                return result
            except Exception as e:
                Logger.error(f"Vectorstore diagnostics resolution failed: {e}", exc_info=True)
                raise

        async def benchmarks_resolver() -> dict[str, Any]:
            try:
                result = {
                    "bootstrap": {
                        "provider_initialized": provider_runtime.initialized,
                        "vectorstore_initialized": vectorstore_runtime.initialized,
                    }
                }
                Logger.debug("Benchmarks resolved successfully")
                return result
            except Exception as e:
                Logger.error(f"Benchmarks resolution failed: {e}", exc_info=True)
                raise

        context = ServiceContext(
            service_name=settings.app_name,
            service_version=settings.app_version,
            provider=provider_runtime.name,
            available_providers=SUPPORTED_PROVIDERS,
            vectorstore=vectorstore_runtime.backend,
            available_vectorstores=SUPPORTED_VECTORSTORES,
            mock_mode=settings.mock_mode,
            debug_mode=settings.app_debug,
            cors_enabled=settings.enable_cors,
            masked_secrets=settings.masked_secrets(),
            settings=settings.operational_settings(),
            metrics_collector=metrics_collector,
            health_checks=(configuration_check,),
            diagnostics_checks=(configuration_check,),
            provider_status_resolver=provider_status_resolver,
            vectorstore_status_resolver=vectorstore_status_resolver,
            provider_diagnostics_resolver=provider_diagnostics_resolver,
            vectorstore_diagnostics_resolver=vectorstore_diagnostics_resolver,
            benchmarks_resolver=benchmarks_resolver,
        )
        
        Logger.info(f"Service context built successfully for provider: {provider_runtime.name}, vectorstore: {vectorstore_runtime.backend}")
        return context
        
    except Exception as e:
        Logger.error(f"Failed to build service context: {e}", exc_info=True)
        raise
