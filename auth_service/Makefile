up:
	docker compose up -d --build

down:
	docker compose down

test:
	docker compose -f tests/docker-compose.yaml up --build

test_down:
	docker compose -f tests/docker-compose.yaml down

test_local:
	pytest tests/src -o log_cli=true -s

run_local:
	uvicorn src.main:app --reload

migrate:
	docker compose exec auth_backend alembic upgrade head
