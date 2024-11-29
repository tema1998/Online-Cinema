#!/usr/bin/env bash

gunicorn -k uvicorn.workers.UvicornWorker core.main:app --bind 0.0.0.0:8080
