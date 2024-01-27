.PHONY: check
check:
	ruff format .
	ruff check . --fix

.PHONY: test
test:
	pytest -v -rs -n auto --cov=core --cov-report=term-missing --cov-fail-under=80

.PHONY: migrate
migrate:
	python manage.py migrate $(filter-out $@,$(MAKECMDGOALS))

.PHONY: migrations
migrations:
	python manage.py makemigrations

.PHONY: run
run:
	python manage.py runserver

.PHONY: show_urls
show_urls:
	python manage.py show_urls

.PHONY: shell
shell:
	python manage.py shell

.PHONY: superuser
superuser:
	python manage.py createsuperuser

.PHONY: up-depenencies-only
up-depenencies-only:
	test -f .env || touch .env
	docker-compose -f docker-compose.dev.yml up -d --build --force-recreate db

.PHONY: load-fixtures
load-fixtures:
	python manage.py loaddata anagram
