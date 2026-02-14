# Makefile template for ap-* projects
# Replace <name> with the project name (e.g., ap-cull-light -> cull_light)

.PHONY: install install-dev install-no-deps uninstall clean format lint typecheck test test-verbose coverage default

PYTHON := python

default: format lint typecheck test coverage

install:
	$(PYTHON) -m pip install .

install-dev:
	$(PYTHON) -m pip install -e ".[dev]"

install-no-deps:
	$(PYTHON) -m pip install -e . --no-deps

uninstall:
	$(PYTHON) -m pip uninstall -y ap-<name>

clean:
	rm -rf build/ dist/ *.egg-info
	find . -type d -name __pycache__ -exec rm -r {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true

format: install-dev
	$(PYTHON) -m black ap_<name> tests

lint: install-dev
	$(PYTHON) -m flake8 --max-line-length=88 --extend-ignore=E203,W503 ap_<name> tests

typecheck: install-dev
	$(PYTHON) -m mypy ap_<name>

test: install-dev
	$(PYTHON) -m pytest

test-verbose: install-dev
	$(PYTHON) -m pytest -v

coverage: install-dev
	$(PYTHON) -m pytest --cov=ap_<name> --cov-report=term
