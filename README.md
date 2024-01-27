# Django Starter

This is a demo project for various tasks related to Anagrams.

## Requirements

- **Django** - web framework
- **pip-tools** - package manager

## Other tools used
- **Makefile** - for running commands conveniently
- **pyproject.toml** - for related tool settings

## Installation and Usage

Install dependencies:
```bash
pip install pip-tools
```
```bash
pip-compile requirements/requirements.dev.in
```
```bash
pip-sync requirements/requirements.dev.txt
```


Start the database:
```bash
docker compose -f docker-compose.dev.yml up db -d
```

Apply migrations:
```bash
make migrate
```

Create superuser:
```bash
make superuser
```

Run the server:
```bash
make run
```


## License

[MIT](https://choosealicense.com/licenses/mit/)
