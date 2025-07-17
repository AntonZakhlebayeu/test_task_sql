FROM python:3.11-slim as builder

WORKDIR /app

RUN pip install --no-cache-dir poetry==1.7.1

COPY pyproject.toml poetry.lock ./

RUN poetry config virtualenvs.create false && \
    poetry install --no-root --only main

COPY . .

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]