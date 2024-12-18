FROM python:3.10-slim-buster

# Set up environment variables
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 - \
    && ln -s /root/.local/bin/poetry /usr/local/bin/poetry

COPY /base_config/ ./base_config/

# Set the working directory
WORKDIR /billing_worker

# Copy Poetry configuration files
COPY /billing_worker/pyproject.toml /billing_worker/poetry.lock ./

# Install Poetry and project dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-root --no-interaction --no-ansi

# Copy the application code
COPY /billing_worker/ .

# Ensure the Python path includes the application directory
ENV PYTHONPATH="/"

# Start the consumer service
CMD ["python", "main.py"]


