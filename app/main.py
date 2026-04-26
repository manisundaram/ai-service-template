from __future__ import annotations

from fastapi.encoders import jsonable_encoder
from ai_service_kit.health import SimpleHealthResponse, check_health, get_diagnostics, get_metrics, ping_service
from ai_service_kit.logging import setup_enhanced_logging, LoggingMiddleware, Logger
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .bootstrap import build_service_context, debug_snapshot
from .config import get_settings


def create_app() -> FastAPI:
    # Setup enhanced logging first
    setup_enhanced_logging()
    
    settings = get_settings()
    service_context = build_service_context(settings)

    app = FastAPI(title=settings.app_name, debug=settings.app_debug)
    app.state.settings = settings
    app.state.service_context = service_context
    
    Logger.info(f"Starting {settings.app_name} v{settings.app_version} in {settings.app_env} mode")

    # Add logging middleware first (after CORS)
    if settings.enable_cors and settings.cors_origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.cors_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    
    # Add logging middleware for request correlation and tracking
    app.add_middleware(LoggingMiddleware)

    @app.get("/ping")
    async def ping() -> dict[str, object]:
        try:
            Logger.debug("Ping endpoint called")
            result = ping_service(app.state.service_context)
            Logger.debug("Ping endpoint completed successfully")
            return jsonable_encoder(result)
        except Exception as e:
            Logger.error(f"Ping endpoint failed: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Internal server error")

    @app.get("/health")
    async def health() -> dict[str, object]:
        try:
            Logger.debug("Health check endpoint called")
            result = await check_health(app.state.service_context)
            # Convert to dict for logging and jsonable_encoder
            result_dict = jsonable_encoder(result)
            status = result_dict.get('status', 'unknown')
            Logger.info(f"Health check completed with status: {status}")
            return result_dict
        except Exception as e:
            Logger.error(f"Health check failed: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Health check failed")

    @app.get("/diagnostics")
    async def diagnostics() -> dict[str, object]:
        try:
            Logger.debug("Diagnostics endpoint called")
            result = await get_diagnostics(app.state.service_context)
            # Convert to dict for logging and jsonable_encoder
            result_dict = jsonable_encoder(result)
            total_checks = result_dict.get('summary', {}).get('total_checks', 0)
            Logger.info(f"Diagnostics completed with {total_checks} checks")
            return result_dict
        except Exception as e:
            Logger.error(f"Diagnostics failed: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Diagnostics failed")

    @app.get("/metrics")
    async def metrics() -> dict[str, object]:
        try:
            Logger.debug("Metrics endpoint called")
            result = get_metrics(app.state.service_context)
            Logger.debug("Metrics endpoint completed successfully")
            return jsonable_encoder(result)
        except Exception as e:
            Logger.error(f"Metrics collection failed: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Metrics collection failed")

    @app.get("/debug/config")
    async def debug_config() -> dict[str, object]:
        try:
            Logger.debug("Debug config endpoint called")
            result = {
                "app": dict(settings.masked_debug_config()),
                "bootstrap": debug_snapshot(app.state.service_context),
            }
            Logger.debug("Debug config endpoint completed successfully")
            return jsonable_encoder(result)
        except Exception as e:
            Logger.error(f"Debug config failed: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Debug config failed")

    return app


app = create_app()
