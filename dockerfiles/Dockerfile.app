FROM python:3.11.10-slim-bullseye

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-cache

ENV PROMETHEUS_MULTIPROC_DIR=/tmp/prometheus_multiproc_dir
RUN mkdir -p $PROMETHEUS_MULTIPROC_DIR

WORKDIR /app

#COPY alembic.ini .
#COPY migrations/ migrations/
COPY src/ .

#CMD ["sh", "-c", "alembic upgrade head && python main.py"]
CMD ["sh", "-c", "uv run python main.py"]
