FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:0.8.22 /uv /uvx /bin/

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends default-jre-headless \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/src
ENV UV_LINK_MODE=copy
ENV PATH=/app/.venv/bin:$PATH

COPY pyproject.toml README.md /app/
COPY src /app/src

RUN uv sync --no-dev --no-editable

ENTRYPOINT ["python", "-m", "faturama.interface.worker.entrypoint"]
