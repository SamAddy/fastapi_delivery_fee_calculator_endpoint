# Stage 1: Build environment
FROM python:3.11 AS builder

WORKDIR /code

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY . .

# Stage 2: Production environment
FROM python:3.11-slim

WORKDIR /app

COPY --from=builder /code /app

EXPOSE 3100

CMD ["gunicorn", "main:app"]