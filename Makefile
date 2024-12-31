run:
	docker compose up

down:
	docker compose down

test-user:
	docker compose run app sh -c "pytest --capture=no users/tests/test_users.py"

test-storage:
	docker compose run app sh -c "pytest --capture=no storage/tests/test_storage.py"

test-tree:
	docker compose run app sh -c "pytest --capture=no share/tests/test_parser.py"

build:
	docker compose build
