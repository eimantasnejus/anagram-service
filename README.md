# Anagram API

## Intro

This is a demo project for various tasks related to anagrams (anagrams - group of words with same letters, 
e.g. (read, dear, dare)).

It's a Django project with Postgres as a database. Preferable way is to use Docker for the database 
(fewer problems with OS specific setup) and running the Django app locally (a touch faster and easier IDE setup 
(tests, debug, etc.)).

To make project more interesting - Database can be populated with data from `dictionary.txt` file which contains all
English words (or at least ~235k of them). This way we can test the performance of the app with a lot of data.

At the moment there are no artificial limitations on the API endpoints, just a few "sanity checks":
- Some endpoints might return tens of thousands of records, so pagination is used to limit the response size there
- Longest word that can be added is 100 characters long (but longest word in the English language is 45 characters
  long, so that should not be a problem)
- Currently copies of the same word can be added to the database, but that can be easily changed (if needed) by adding
  a unique constraint to the `word` field in the `Word` model
- The biggest tradeoff in the project is long load time of the `dictionary.txt` file to the database in favor of fast performance later on:
  - It takes around 3 minutes to prepare and load the demo data to the database (on MacBook Pro M1 Pro 32GB RAM)
  - However, this longer initial wait time pays off in the long run - all the API endpoints are fast and code is rather simple.

## Requirements

- **Docker** - for running the Postgres database
- **pip-tools** - package manager to manage Django dependencies locally

## Installation
Start the database in detached mode:
```bash
docker compose -f docker-compose.dev.yml up db -d
```

Install dev environment dependencies:
```bash
pip install pip-tools
```
```bash
pip-compile requirements/requirements.dev.in
```
```bash
pip-sync requirements/requirements.dev.txt
```


Apply migrations:
```bash
make migrate
```

Run the server:
```bash
make run
```
## Useful commands
### Load dictionary.txt data to database
This repository has both `dictionary.txt` and `anagram.json` files. You can jump straight to `make load-fixtures` command if you want to skip the process of creating the fixtures.

If starting from zero:

Copy `dictionary.txt` file in the root of the project. From that - create a json file with fixtures using script:
```bash
python dictionary_to_anagram_fixtures.py
```
This will create a `anagram/fixtures/anagram.json` file. Then load the data to database:
```bash
make load-fixtures
```
Don't worry if it takes a while. It's a big file. Usual wait time is around 3 minutes.

Afterward you can check the data in the database:
```bash
make shell
```
```python
from anagram.models import Word
Word.objects.count()
```
Should return ~235k records.
### Create and apply migrations
```bash
make migrations
```
```bash
make migrate
```

### Migrate to a specific migration
`make migrate <app_name> <migration_number>`
e.g.:
`make migrate anagram 0001`

### Run tests
Minimal test coverage is set to 80%. But it's 100% at the moment. To run tests:
```bash
make test
```

### Check and fix code style
`ruff` is the new cool kid on the block. It's replacing `black`, `isort` and `flake8`. It's used to check and fix code style unbelievably fast.
```bash
make check
```

### Makefile
There are more useful commands in the `Makefile`. Check it out.

## Roadmap / TODOs / Development ideas
- Dockerize Django app
- Add CI/CD to the project (Github Actions)
- Add Django management command to load data from `dictionary.txt` file
- Add Indexes to make the search faster (experiment with different indexes, app is pretty snappy as it is, maybe it's not needed)
- Convert some traditional model fields to GeneratedFields to save space (at least experiment to see if it's worth it)
- Find a way to upload `dictionary.txt` file to the database faster (currently it takes ~3 minutes)
- Unify endpoint structure (remove `.json` from the end of the endpoints)
- Add some more complex functionality, more models and relations
- Add authentication and authorization, currently all endpoints are open to the public
- Some heavier tasks could use celery and be async
- Add Sentry for error tracking
- Monitoring (e.g. Prometheus, Grafana, Datadog, etc.)
- Use environment variables for sensitive data (e.g. SECRET_KEY, DB credentials, etc.)
- Setup for production (nginx, gunicorn, etc.)
- File Import/Export - add new words to the database by simply uploading a file, export words to a file
- Implement Django Templates for frontend
- Use HTMX for dynamic frontend once Django Templates are implemented
- Some cool charts and graphs to visualize the data, statistics, etc.
- Put project on the cloud (AWS, GCP, etc.)
- Once on cloud, implement IAC (Terraform, CDK, Pulumi, etc.)
- ...


## License

[MIT](https://choosealicense.com/licenses/mit/)
