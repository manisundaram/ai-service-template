# ai-service-template

`ai-service-template` is a production-ready FastAPI application template for building AI-facing services on top of the shared `ai-service-kit` library. It provides a complete operational foundation with health monitoring, diagnostics, metrics, optimized ping endpoints, and **enhanced production logging** with cloud provider integration.

## What this template is for

Use this template when you want a production-shaped FastAPI service that can consume provider, health, and vectorstore abstractions from `ai-service-kit` without re-implementing those contracts in each new project. The template includes comprehensive operational endpoints for monitoring, debugging, performance tracking, and **enterprise-grade logging** with cloud provider support.

## How it uses ai-service-kit

The template imports shared contracts and helpers from `ai_service_kit`, including:

- **Provider & Vectorstore**: Registry and factory wiring for bootstrap setup
- **Health Monitoring**: Comprehensive health checks with status aggregation
- **Lightweight Ping**: Optimized ping service for rapid health checks
- **Diagnostics**: Deep system analysis with performance benchmarks
- **Metrics**: Operational metrics collection for monitoring dashboards
- **Enhanced Production Logging**: Structured JSON logs, request correlation, and cloud provider integration (AWS CloudWatch, Datadog, Azure Monitor, Google Cloud Logging)

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
- **`GET /debug/config`** - Configuration introspection with masked secrets

## Enhanced Production Logging

The template includes enterprise-grade logging features powered by `ai-service-kit`:

### **Core Features**

- **Structured JSON Logs**: Production-ready log format for easy parsing and analysis
- **Request Correlation**: Automatic request tracking and correlation across services
- **Multi-Level Logging**: Separate log levels for console, file, and error outputs
- **Automatic Log Rotation**: Configurable file size limits and backup retention
- **Static Logger Interface**: Simple `Logger.info()`, `Logger.error()` usage throughout codebase

### **Cloud Provider Integration**

- **AWS CloudWatch**: Cost-optimized error-only logging for production monitoring
- **Datadog**: Rich dashboards with info-level logging for comprehensive insights
- **Azure Monitor**: Enterprise monitoring integration for Azure environments
- **Google Cloud Logging**: Native GCP log aggregation and analysis

### **Configuration Example**

```bash
# Enable structured JSON logs for production
LOG_STRUCTURED=true
LOG_LEVEL=INFO

# Enable cloud logging (comma-separated)
CLOUD_LOGGING_PROVIDERS=aws,datadog

# AWS CloudWatch (errors only)
AWS_LOGGING_ENABLED=true
AWS_LOGGING_LEVEL=ERROR
AWS_LOG_GROUP=/ai-service-template/production

# Datadog (rich dashboards)
DATADOG_LOGGING_ENABLED=true
DATADOG_LOGGING_LEVEL=INFO
DATADOG_API_KEY=your-datadog-api-key
```

## Install dependencies

Install the application dependencies, including the local editable sibling dependency on `ai-service-kit`:

```bash
pip install -r requirements.txt
```

### Optional: Cloud Provider Dependencies

For production environments with cloud logging, install additional dependencies as needed:

```bash
# For AWS CloudWatch logging
pip install boto3>=1.26.0

# For Datadog logging
pip install datadog>=0.44.0

# For Azure Monitor logging
pip install applicationinsights>=0.11.0

# For Google Cloud Logging
pip install google-cloud-logging>=3.0.0

# Install all cloud providers at once
pip install boto3>=1.26.0 applicationinsights>=0.11.0 google-cloud-logging>=3.0.0 datadog>=0.44.0
```

## Configure environment variables

Create your local environment file from the example:

```bash
copy .env.example .env
```

Update `.env` with:

- **Provider credentials** and runtime values you want to use
- **Enhanced logging configuration** including log levels, structured logging, and file rotation
- **Cloud provider settings** (optional) for production logging integration

Key configuration sections:

- **Application Settings**: `APP_NAME`, `APP_ENV`, `APP_DEBUG`
- **Provider Configuration**: `PROVIDER_TYPE`, API keys for OpenAI/Gemini/Claude
- **Enhanced Logging**: `LOG_LEVEL`, `LOG_STRUCTURED`, `LOG_DIR`, cloud provider settings
- **CORS Configuration**: `ENABLE_CORS`, `CORS_ORIGINS`

## Run the app

Start the FastAPI application with Uvicorn:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

The application will be available at `http://localhost:8000` with automatic API documentation at `/docs`.

### Production Logging Output

In production mode (`APP_ENV=production`), you'll see structured JSON logs like:

```
2026-04-26 18:30:24 [INFO] [ai-service] app.main - Starting AI Service Template v0.1.0 in development mode
2026-04-26 18:31:39 [INFO] [ai-service] app.main - Health check completed with status: healthy
```

Cloud provider integrations automatically forward logs to your configured services.

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
