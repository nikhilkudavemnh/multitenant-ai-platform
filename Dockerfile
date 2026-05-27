FROM python:3.14-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app
ENV VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH"

COPY pyproject.toml uv.lock ./
RUN uv sync --no-dev --frozen --no-install-project

COPY src ./src
COPY frontend ./frontend

EXPOSE 8001

CMD ["gunicorn", "src.main:app", \
     "-k", "uvicorn.workers.UvicornWorker", \
     "--workers", "2", \
     "--worker-connections", "20", \
     "--bind", "0.0.0.0:8001", \
     "--graceful-timeout", "30", \
     "--timeout", "60", \
     "--keep-alive", "2", \
     "--max-requests", "500", \
     "--max-requests-jitter", "50", \
     "--preload"]
