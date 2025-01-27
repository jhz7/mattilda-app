start:
	docker-compose up -d --build app-server

logs.server:
	docker-compose logs -f app-server

logs.db:
	docker-compose logs -f db

logs.cache:
	docker-compose logs -f cache

run.migrations:
	docker-compose exec app-server alembic revision --autogenerate -m "migration"
	docker-compose exec app-server alembic upgrade head
