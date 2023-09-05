# First stage: Setup the python environment
FROM python:3.9-slim as builder
RUN apt-get update && apt-get install -y gcc libffi-dev g++ curl gnupg2 lsb-release wget

# Set Environment Variables
ARG NEXUS_PYPI_USER
ENV NEXUS_PYPI_USER=$NEXUS_PYPI_USER

ARG NEXUS_PYPI_PASSWD
ENV NEXUS_PYPI_PASSWD=$NEXUS_PYPI_PASSWD

ARG NEXUS_PYPI_INDEX_URL
ENV NEXUS_PYPI_INDEX_URL=$NEXUS_PYPI_INDEX_URL

WORKDIR /app
COPY ./src ./src
COPY ./scripts ./scripts

# Install dependencies:
COPY ./pyproject.toml .
COPY ./poetry.lock .

# Setup Poetry
RUN pip install poetry
RUN poetry config virtualenvs.create false
RUN poetry source add --secondary cloudscent https://$NEXUS_PYPI_INDEX_URL
RUN poetry config http-basic.cloudscent $NEXUS_PYPI_USER $NEXUS_PYPI_PASSWD
RUN poetry install --no-root --no-dev

# Make sure start script is executable
RUN chmod +x ./scripts/start.sh

CMD ["./scripts/start.sh"]