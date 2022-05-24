python_paths = src/ tests/

all: nice pytest

isort:
	isort $(python_paths)

black:
	black $(python_paths)

format: isort black

mypy:
	mypy --strict $(python_paths)

flake8:
	flake8 $(python_paths)

checks: mypy flake8

nice: format checks

pytest:
	pytest
