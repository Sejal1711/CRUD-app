FROM python:3.11-slim

WORKDIR /app

# Install Poetry
RUN pip install poetry

# Copy dependency files
COPY pyproject.toml poetry.lock* ./

# Install production dependencies only
RUN poetry config virtualenvs.create false \
    && poetry install --only main --no-interaction --no-ansi

COPY . .

RUN mkdir -p logs

# Cloud Run sets $PORT automatically — default 8080
ENV PORT=8080

EXPOSE 8080

# Use shell form to read $PORT at runtime
CMD uvicorn app.main:app --host 0.0.0.0 --port $PORT
