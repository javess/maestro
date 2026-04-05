FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN pip install --no-cache-dir uv

COPY pyproject.toml README.md ./
COPY src ./src
COPY policies ./policies
COPY prompts ./prompts
COPY skills ./skills
COPY examples ./examples

RUN uv sync --frozen --no-dev || uv sync --no-dev

CMD ["uv", "run", "maestro", "doctor"]

