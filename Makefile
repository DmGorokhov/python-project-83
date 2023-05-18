install:
		poetry install

dev:
		poetry run flask --app page_analyzer:app run

PORT ?= 8000
start:
		poetry run gunicorn -w 5 -b 0.0.0.0:$(PORT) page_analyzer:app

publish:
		poetry publish --dry-run

package-install:
		python3 -m pip install --user dist/*.whl

package-reinstall:
		python3 -m pip install --user --force-reinstall dist/*.whl

lint:
		poetry run flake8 page_analyzer

test:
		poetry run pytest

test-cov:
		poetry run pytest --cov=gendiff

selfcheck:
		poetry check

#check: selfcheck test lint

.PHONY: install test lint selfcheck check build