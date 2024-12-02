# Use an official Python runtime as a base image
FROM python:3.10.7-slim-buster

# Install system dependencies
RUN apt-get update && \
    apt-get install --no-install-recommends -y \
    build-essential \
    wget \
    make \
    gcc \
    libpq-dev \
    && apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set the working directory for dependencies
WORKDIR /billing_rabbitmq_init

# Copy Poetry configuration files
COPY /billing_rabbitmq_init/pyproject.toml /billing_rabbitmq_init/poetry.lock ./

# Install Poetry and dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-root --no-interaction --no-ansi

# Set the working directory
WORKDIR /billing_rabbitmq_init

# Copy the rest of the application code
COPY /billing_rabbitmq_init/ .
COPY /base_config/ /base_config/

# Set the PYTHONPATH environment variable
ENV PYTHONPATH="/"

# Command to run the RabbitMQ initialization script
CMD ["python3", "main.py"]