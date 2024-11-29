FROM python:3.12

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
WORKDIR /billing_service
COPY /.env ./

# Copy Poetry configuration files
COPY /billing_service/poetry.lock /billing_service/pyproject.toml ./
#COPY /auth_service/alembic /auth_service/alembic.ini ./

# Install Poetry and project dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-root

# Copy the rest of the application code
COPY ./billing_service/ ./

# Set the PYTHONPATH environment variable

# Expose the port that the application will run on
EXPOSE 8082

ENTRYPOINT ["/bin/bash", "start.sh"]
