#!/usr/bin/env bash
python3 /tests/functional/utils/wait_for_es.py
python3 /tests/functional/utils/wait_for_redis.py
pytest /tests/functional/src -o log_cli=true -s
