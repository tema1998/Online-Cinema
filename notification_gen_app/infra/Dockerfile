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
    wait-for-it && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY /base_config/ ./base_config/

# Set the working directory
WORKDIR /notification_gen_app

# Copy environment file
COPY .env ./

# Copy Poetry configuration files
COPY /notification_gen_app/pyproject.toml /notification_gen_app/poetry.lock ./

# Install Poetry and project dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-root --no-interaction --no-ansi

# Copy the rest of the application code
COPY /notification_gen_app/ .

# Set the PYTHONPATH environment variable
ENV PYTHONPATH="/"

# Expose the port the application will run on
EXPOSE 8080

# Command to run the FastAPI application with uvicorn
CMD ["uvicorn", "notification_gen_app.main:app", "--host", "0.0.0.0", "--port", "8080", "--reload"]