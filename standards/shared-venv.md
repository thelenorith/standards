# Shared Virtual Environment

Standard for using Python virtual environments across ap-* projects, both standalone and in the ap-base monorepo.

## Rationale

- **Isolation** - Never install project dependencies into the system Python
- **Reproducibility** - Everyone gets the same environment per `pyproject.toml`
- **Monorepo efficiency** - One venv for all submodules avoids redundant installs of shared dependencies (astropy, xisf, etc.)
- **Simplicity** - `make install-dev` is all you need; venv creation is automatic

## How It Works

Each submodule Makefile declares:

```makefile
VENV_DIR ?= .venv
PYTHON := $(VENV_DIR)/bin/python
```

The `?=` operator means "use this default unless already set." This is the key mechanism:

- **Standalone** (`cd ap-cull-light && make install-dev`): `VENV_DIR` defaults to `.venv`, creating a local venv in `ap-cull-light/.venv/`
- **Monorepo** (`cd ap-base && make install-all`): ap-base sets `VENV_DIR=$(CURDIR)/.venv` and passes it to submodule Makefiles, so all submodules share `ap-base/.venv/`

## Standalone Usage

When working on a single repo:

```bash
cd ap-cull-light
make install-dev    # Creates .venv/, installs package + dev deps
make test           # Runs tests using .venv/bin/python
make default        # Runs all checks using .venv/bin/python
```

The venv is created automatically on first `make install-dev`. No manual `python -m venv` needed.

## Monorepo Usage (ap-base)

When working across multiple repos in ap-base:

```bash
cd ap-base
make install-all    # Creates .venv/, installs ALL submodules (editable)
```

This creates a single `.venv/` at the ap-base root with every ap-* package installed in editable mode. Changes to any submodule's source are immediately reflected.

To run checks across all submodules using the shared venv:

```bash
make check-all      # Runs default target in every submodule
```

To run checks in a single submodule using the shared venv:

```bash
make -C ap-cull-light VENV_DIR=$(pwd)/.venv default
```

### Cross-repo development

The shared venv makes cross-repo development seamless. When modifying ap-common and testing in ap-cull-light:

```bash
cd ap-base
make install-all        # All packages installed editable
# Edit ap-common/ap_common/constants.py
# Changes are immediately visible in ap-cull-light
make -C ap-cull-light VENV_DIR=$(pwd)/.venv test
```

No need for `install-no-deps` tricks - editable installs in a shared venv handle this naturally.

## Makefile Pattern

The venv is managed as a Make prerequisite. The `$(VENV_DIR)/bin/python` file is the target - Make only creates the venv if it does not already exist:

```makefile
VENV_DIR ?= .venv
PYTHON := $(VENV_DIR)/bin/python

$(VENV_DIR)/bin/python:
	python3 -m venv $(VENV_DIR)

install-dev: $(VENV_DIR)/bin/python
	$(PYTHON) -m pip install -e ".[dev]"
```

See [templates/Makefile](templates/Makefile) for the full template.

## CI Compatibility

GitHub Actions workflows do not need changes. The `actions/setup-python` action puts a specific Python version on `PATH`. When the Makefile runs `python3 -m venv`, it uses that version. The venv is created in the CI workspace and discarded after the job.

## What to Avoid

- **Do not activate the venv in Makefiles** - Use `$(VENV_DIR)/bin/python` directly. Shell `source activate` does not persist across Make recipe lines.
- **Do not use `VIRTUAL_ENV` environment variable** to detect existing venvs. Use the `VENV_DIR` Makefile variable for explicit control.
- **Do not install into system Python** - The Makefile template always installs into a venv.
- **Do not create the venv manually** - Let `make install-dev` handle it.
