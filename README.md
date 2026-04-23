# ai-service-template

`ai-service-template` is a production-ready FastAPI application template for building AI-facing services on top of the shared `ai-service-kit` library. It provides a complete operational foundation with health monitoring, diagnostics, metrics, and optimized ping endpoints.

## What this template is for

Use this template when you want a production-shaped FastAPI service that can consume provider, health, and vectorstore abstractions from `ai-service-kit` without re-implementing those contracts in each new project. The template includes comprehensive operational endpoints for monitoring, debugging, and performance tracking.

## How it uses ai-service-kit

The template imports shared contracts and helpers from `ai_service_kit`, including:

- **Provider & Vectorstore**: Registry and factory wiring for bootstrap setup
- **Health Monitoring**: Comprehensive health checks with status aggregation  
- **Lightweight Ping**: Optimized ping service for rapid health checks
- **Diagnostics**: Deep system analysis with performance benchmarks
- **Metrics**: Operational metrics collection for monitoring dashboards
- **Configuration**: Environment-based settings with secret masking utilities

This keeps the application layer thin while `ai-service-kit` acts as the shared contract layer.

## Project structure

```text
.
├── .env.example              # Environment configuration template
├── pyproject.toml           # Python project configuration
├── requirements.txt         # Python dependencies
├── app/                     # Application source code
│   ├── __init__.py         
│   ├── bootstrap.py         # ServiceContext builder with health resolvers
│   ├── config.py           # Settings management with secret masking
│   └── main.py             # FastAPI app with operational endpoints
└── tests/                   # Test suite
    └── test_app.py         # Endpoint validation tests
```

## Operational Endpoints

The template provides comprehensive operational endpoints for production monitoring:

- **`GET /ping`** - Lightweight health check optimized for load balancers (returns `ok` status)
- **`GET /health`** - Comprehensive health report with provider/vectorstore status checks
- **`GET /diagnostics`** - Deep system analysis with performance benchmarks and provider tests
- **`GET /metrics`** - Prometheus-style metrics for monitoring dashboards
- **`GET /debug/config`** - Configuration introspection with masked secrets (debug mode only)
## Install dependencies

Install the application dependencies, including the local editable sibling dependency on `ai-service-kit`:

```bash
pip install -r requirements.txt
```

## Configure environment variables

Create your local environment file from the example:

```bash
copy .env.example .env
```

Update `.env` with the provider credentials and runtime values you want to use.

## Run the app

Start the FastAPI application with Uvicorn:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

The application will be available at `http://localhost:8000` with automatic API documentation at `/docs`.

### Endpoint Performance Notes

- **`/ping`**: Uses optimized `ping_service()` for sub-millisecond responses - ideal for load balancer health checks
- **`/health`**: Performs comprehensive checks including provider connectivity - use for detailed monitoring
- **`/diagnostics`**: Includes performance benchmarks and deep analysis - use for troubleshooting

## Run tests

Execute the test suite with pytest:

```bash
pytest
```

All tests validate endpoint functionality, response schemas, and service integration. The test suite includes validation for all operational endpoints and their expected response formats.
