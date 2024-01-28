.PHONY: check
check:
	ruff format .
	ruff check . --fix

.PHONY: test
test:
	pytest -v -rs -n auto --cov=anagram --cov-report=term-missing --cov-fail-under=80  --reuse-db

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

.PHONY: load-fixtures
load-fixtures:
	python manage.py loaddata word
