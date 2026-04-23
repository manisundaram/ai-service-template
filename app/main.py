from __future__ import annotations

from fastapi.encoders import jsonable_encoder
from ai_service_kit.health import SimpleHealthResponse, check_health, get_diagnostics, get_metrics, ping_service
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .bootstrap import build_service_context, debug_snapshot
from .config import get_settings


def create_app() -> FastAPI:
    settings = get_settings()
    service_context = build_service_context(settings)

    app = FastAPI(title=settings.app_name, debug=settings.app_debug)
    app.state.settings = settings
    app.state.service_context = service_context

    if settings.enable_cors and settings.cors_origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.cors_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    @app.get("/ping")
    async def ping() -> dict[str, object]:
        return jsonable_encoder(ping_service(app.state.service_context))

    @app.get("/health")
    async def health() -> dict[str, object]:
        return jsonable_encoder(await check_health(app.state.service_context))

    @app.get("/diagnostics")
    async def diagnostics() -> dict[str, object]:
        return jsonable_encoder(await get_diagnostics(app.state.service_context))

    @app.get("/metrics")
    async def metrics() -> dict[str, object]:
        return jsonable_encoder(get_metrics(app.state.service_context))

    @app.get("/debug/config")
    async def debug_config() -> dict[str, object]:
        return jsonable_encoder(
            {
                "app": dict(settings.masked_debug_config()),
                "bootstrap": debug_snapshot(app.state.service_context),
            }
        )

    return app


app = create_app()
