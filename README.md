# FastAPI Authentication Service

A FastAPI-based application for managing user authentication, roles, and permissions, with support for Redis caching, RabbitMQ event handling, and OpenTelemetry instrumentation. The project is containerized with Docker and uses Poetry for dependency management.


A high-performance, modular **FastAPI** microservice featuring:
- **Authentication & Authorization** with API keys and JWT.
- **Redis Caching** for enhanced performance.
- **RabbitMQ** event consumer for asynchronous processing.
- **OpenTelemetry** instrumentation and tracing.
- **PostgreSQL** database integration via SQLAlchemy.
- **Docker** & **Docker Compose** for containerization.
- **Poetry** for dependency management.
- Comprehensive **unit tests** with pytest.

## 📁 Project Structure Overview

- **`Dockerfile`**: Builds the Docker image for the app.  
- **`README.md`**: Project documentation.  
- **`app/`**: Core FastAPI application code.
  - **`main.py`**: Entry point of the app.
  - **`config.py`**, **`db.py`**, **`dependencies.py`**: App settings, database, and dependency setup.
  - **`caching/`**: Redis caching logic.
  - **`events/`**: RabbitMQ consumer and event handling.
  - **`instrumentation/`**: OpenTelemetry tracing setup.
  - **`models/`**: SQLAlchemy models (e.g., users, API keys).
  - **`routers/`**: API endpoints for auth, users, roles, permissions.
  - **`schemas/`**: Pydantic models for requests and responses.
  - **`services/`**: Business logic (auth, roles, permissions, users).
  - **`utils/`**: Helpers for logging, JWT, env loading, etc.
- **`config/otel-collector-config.yaml`**: OpenTelemetry collector config.  
- **`docker-compose.yml`**: Runs app + services (Redis, RabbitMQ).  
- **`poetry.lock`**, **`pyproject.toml`**: Dependency management with Poetry.  
- **`pytest.ini`**: Pytest config.  
- **`redis.conf`**: Redis setup.  
- **`tests/`**: Unit tests for core functionality.


```
.
├── Dockerfile
├── README.md
├── app
│   ├── caching/redis_cache.py
│   ├── config.py
│   ├── db.py
│   ├── dependencies.py
│   ├── events
│   │   ├── consumer.py
│   │   └── rabbitmq.py
│   ├── instrumentation/tracing.py
│   ├── main.py
│   ├── models
│   ├── routers
│   ├── schemas
│   ├── services
│   └── utils
├── config/otel-collector-config.yaml
├── docker-compose.yml
├── otel-collector-config.yaml
├── poetry.lock
├── pyproject.toml
├── pytest.ini
├── redis.conf
└── tests
```

## Prerequisites

- Python 3.9+
- Docker & Docker Compose
- RabbitMQ
- Redis
- PostgreSQL
- Poetry

## CI/CD

This project includes a GitHub Actions workflow for Continuous Integration:

- **Workflow File**: `.github/workflows/ci.yml`
- **Features**:
  - Runs on every push and pull request
  - Installs dependencies using Poetry
  - Lints and runs tests using pytest

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```
2. Install dependencies via Poetry:
   ```bash
   poetry install
   ```
3. Copy environment variables:
   ```bash
   cp .env.example .env
   # Update .env with your settings (database, Redis, RabbitMQ, etc.)
   ```

## Configuration

Environment variables in `.env`:
```
DATABASE_URL=postgresql://user:pass@localhost:5432/dbname
REDIS_URL=redis://localhost:6379/0
RABBITMQ_URL=amqp://guest:guest@localhost:5672/
API_KEY_SECRET=<your-secret>
OTEL_COLLECTOR_URL=http://otel-collector:4317
```

OpenTelemetry Collector config: `config/otel-collector-config.yaml`

## Running the Service

### Locally

```bash
poetry run uvicorn app.main:app --reload
```

### Docker

```bash
docker-compose up --build
```

The API will be available at `http://localhost:8000`.

## API Documentation

Interactive docs:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Testing

Run unit tests with pytest:
```bash
pytest --maxfail=1 --disable-warnings -q
```

## License

MIT License. See `LICENSE` for details.



You can customize the workflow to include additional checks, deployment steps, or notifications.
