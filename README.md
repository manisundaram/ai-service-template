# ai-service-template

## Start Here

Clone this template to create a new FastAPI service. Keep `ai-service-kit` as the shared dependency for reusable infrastructure instead of copying provider, operational, or logging internals into the new repo.

## Documentation Map

- [Setup and Run](#setup-and-run)
- [Provider Configuration](#provider-configuration-important)
- [Logging and Cloud Providers](#logging-provider-activation)
- [Operational Endpoints](#operational-endpoints)
- [Testing](#testing)

## How This Template Uses ai-service-kit

This template intentionally reuses these `ai-service-kit` capabilities:

- provider abstractions
- health, diagnostics, metrics, and ping operational endpoints
- logging middleware and enhanced logging setup
- settings helpers, including the 2-level provider fallback

The app-specific repo keeps only service-local settings, bootstrap wiring, and any future business routes.

## Setup and Run

Install the template and its shared dependency:

```bash
pip install -r requirements.txt
```

Optional cloud logging dependencies:

```bash
pip install boto3>=1.26.0
pip install applicationinsights>=0.11.0
pip install google-cloud-logging>=3.0.0
pip install datadog>=0.44.0
```

Create a local environment file:

```bash
copy .env.example .env
```

Run the service:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

The default app exposes API docs at `http://localhost:8000/docs`.

## Provider Configuration (Important)

This template uses a strict 2-level fallback and nothing else:

1. family-specific key
2. shared provider key

That means each resolved setting follows the pattern below:

- LLM OpenAI API key: `LLM_OPENAI_API_KEY` -> `OPENAI_API_KEY`
- Embedding OpenAI model: `EMBEDDING_OPENAI_MODEL` -> `OPENAI_MODEL`

Use `PROVIDER` when both families should default to the same provider. Override with `LLM_PROVIDER` or `EMBEDDING_PROVIDER` only when you need a split.

Example: same provider for both families

```env
PROVIDER=openai

OPENAI_API_KEY=shared-openai-key
OPENAI_MODEL=gpt-4o-mini

EMBEDDING_OPENAI_MODEL=text-embedding-3-small
```

Example: split provider families

```env
PROVIDER=openai
LLM_PROVIDER=gemini
EMBEDDING_PROVIDER=openai

OPENAI_API_KEY=shared-openai-key
EMBEDDING_OPENAI_MODEL=text-embedding-3-small

LLM_GEMINI_API_KEY=gemini-key
LLM_GEMINI_MODEL=gemini-2.5-flash
```

Supported template provider names are `openai`, `gemini`, and `anthropic`. Legacy `claude` values are normalized to `anthropic` for compatibility.

## Logging Provider Activation

`CLOUD_LOGGING_PROVIDERS` is the only activation mechanism.

Provider-specific settings only configure providers named in that list.

AWS required settings:

- `AWS_LOGGING_LEVEL`
- `AWS_LOG_GROUP`
- `AWS_REGION`

Azure required settings:

- `AZURE_LOGGING_LEVEL`
- `AZURE_CONNECTION_STRING`

GCP required settings:

- `GCP_LOGGING_LEVEL`
- `GCP_PROJECT_ID` when default project discovery is not available

Datadog required settings:

- `DATADOG_LOGGING_LEVEL`
- `DATADOG_API_KEY`

Example:

```env
CLOUD_LOGGING_PROVIDERS=aws,datadog

AWS_LOGGING_LEVEL=ERROR
AWS_LOG_GROUP=/my-service/production
AWS_REGION=us-east-1

DATADOG_LOGGING_LEVEL=INFO
DATADOG_API_KEY=your-datadog-api-key
```

## Operational Endpoints

This template registers the standard `ai-service-kit` operational scaffold:

- `GET /ping`: lightweight uptime probe for load balancers and basic readiness checks
- `GET /health`: service health with configuration and component status
- `GET /diagnostics`: deeper runtime diagnostics and bootstrap benchmark details
- `GET /metrics`: normalized metrics payload from the active metrics collector
- `GET /debug/config`: masked settings snapshot plus bootstrap state

Middleware wiring also comes from `ai-service-kit`, including request logging correlation and CORS setup.

## Testing

Run the full suite with:

```bash
pytest
```

The tests cover:

- 2-level provider fallback behavior
- operational endpoint responses
- cloud logging provider parsing

## Clone Checklist

1. Rename app and service values such as `APP_NAME`, package metadata, and any business-specific module names.
2. Configure shared and family-specific providers using the 2-level fallback model.
3. Configure `CLOUD_LOGGING_PROVIDERS` and required provider credentials.
4. Run tests.
5. Verify `/ping`, `/health`, `/diagnostics`, `/metrics`, and `/debug/config` locally.
