run:
	docker compose up

test-storage:
	docker compose run app sh -c "pytest --capture=no storage/tests/test_storage.py"

build:
	docker compose build
