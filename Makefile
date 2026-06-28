.PHONY: install backend frontend dev test docker-up docker-down

install:
	python3 -m venv .venv
	.venv/bin/pip install -r requirements.txt
	cd frontend && npm install

backend:
	.venv/bin/uvicorn backend.main:app --reload

frontend:
	cd frontend && npm run dev

dev:
	@chmod +x scripts/dev.sh
	@./scripts/dev.sh

test:
	PYTHONPATH=. .venv/bin/python scripts/verify_e2e.py

docker-up:
	docker compose up --build

docker-down:
	docker compose down
