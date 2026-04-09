FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR root
COPY pyproject.toml .
RUN pip install poetry
RUN poetry config virtualenvs.create false
RUN poetry install

WORKDIR src
COPY src/ .
COPY pyproject.toml ./stub.toml

EXPOSE 7070
RUN pip install uvicorn

LABEL org.opencontainers.image.source="https://github.com/odissei-data/dataverse-mapper"
LABEL org.opencontainers.image.description="Service to map any JSON metadata to Dataverse JSON format."
