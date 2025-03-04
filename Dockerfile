# syntax=docker/dockerfile:1

FROM python:3.11-slim

LABEL org.opencontainers.image.description="Delivery Fee Calculator API" \
      org.opencontainers.image.authors="Samuel Addison"

WORKDIR /code

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY . .

RUN python -m pytest tests

EXPOSE 3100

CMD ["gunicorn", "delivery_fee_calculator.main:app"]
