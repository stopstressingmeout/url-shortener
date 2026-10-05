# Start from a small official Python image.
FROM python:3.12-slim

# Copy the uv tool into the image from its official image.
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

ENV PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_PYTHON_DOWNLOADS=never \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app

# 1) Dependencies first. This layer is only rebuilt when these two files change.
COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-dev --no-install-project
# 2) Then the application code (changes often, so it comes later).
COPY app ./app
COPY alembic ./alembic
COPY alembic.ini ./

# Run as a normal user instead of root.
RUN useradd --system --create-home appuser
USER appuser

EXPOSE 8000

# On start: apply database migrations, then launch the server.
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --proxy-headers --forwarded-allow-ips='*'"]