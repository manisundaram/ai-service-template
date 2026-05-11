from __future__ import annotations

from ai_service_kit.health import apply_operational_middleware, register_operational_endpoints
from ai_service_kit.logging import Logger, setup_enhanced_logging
from fastapi import FastAPI

from .bootstrap import build_service_context, debug_snapshot
from .config import get_settings


def create_app() -> FastAPI:
    settings = get_settings()
    setup_enhanced_logging(service_name=settings.app_name, environment=settings.app_env)

    service_context = build_service_context(settings)

    app = FastAPI(title=settings.app_name, debug=settings.app_debug)
    app.state.settings = settings
    app.state.service_context = service_context

    Logger.info(f"Starting {settings.app_name} v{settings.app_version} in {settings.app_env} mode")

    apply_operational_middleware(
        app,
        enable_cors=settings.enable_cors,
        cors_origins=settings.cors_origins,
        enable_logging_middleware=True,
    )

    register_operational_endpoints(
        app,
        context_getter=lambda current_app: current_app.state.service_context,
        settings_snapshot_getter=lambda current_app: current_app.state.settings.masked_debug_config(),
        bootstrap_snapshot_getter=lambda current_app: debug_snapshot(current_app.state.service_context),
    )

    return app


app = create_app()
