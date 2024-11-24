FROM python:3.10.7-slim-buster

# Install necessary packages
RUN apt-get update && \
    apt-get install --no-install-recommends -y \
    build-essential \
    wget \
    make \
    gcc \
    libpq-dev \
    wait-for-it && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /src
COPY /.env ./

# Copy Poetry configuration files
COPY /auth_service/poetry.lock /auth_service/pyproject.toml ./
COPY /auth_service/alembic /auth_service/alembic.ini ./

# Install Poetry and project dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-root

# Copy the rest of the application code
COPY ./auth_service/ .

# Set the PYTHONPATH environment variable
ENV PYTHONPATH=/src

# Expose the port that the application will run on
EXPOSE 8080

ENTRYPOINT ["/bin/bash", "start.sh"]
