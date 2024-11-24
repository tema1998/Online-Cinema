#!/usr/bin/env bash
python3 /tests/utils/wait_for_redis.py
python3 /tests/utils/wait_for_pg.py
pytest /tests/src -o log_cli=true -s
