FROM python:3.9-alpine
WORKDIR /app
RUN apk add --no-cache \
    gcc \
    musl-dev \
    libffi-dev \
    poetry

COPY pyproject.toml poetry.lock /app/
RUN poetry install --no-interaction --no-dev
COPY . /app
EXPOSE 8080
CMD ["poetry","run","gunicorn", "-b", "0.0.0.0:8080", "src:app"]
