FROM python:3.12-slim

WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN pip install uv && uv sync --locked --no-dev --no-install-project
COPY alembic.ini ./alembic.ini
COPY alembic ./alembic
COPY datasets ./datasets
COPY src ./src
RUN uv sync --locked --no-dev
EXPOSE 8000
CMD ["uv", "run", "uvicorn", "email_agent.api:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000"]
