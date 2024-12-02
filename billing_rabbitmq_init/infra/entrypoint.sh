#!/bin/bash

# Ensure `envsubst` is installed
if ! command -v envsubst &> /dev/null; then
  echo "Installing envsubst..."
  apt-get update && apt-get install -y --no-install-recommends gettext-base && apt-get clean && rm -rf /var/lib/apt/lists/*
fi

# Generate the RabbitMQ configuration file
echo "Generating RabbitMQ configuration..."
envsubst < /etc/rabbitmq/rabbitmq.conf.template > /etc/rabbitmq/rabbitmq.conf

# Start RabbitMQ server
exec rabbitmq-server