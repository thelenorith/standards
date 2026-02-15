# Shared Virtual Environment

Standard for using Python virtual environments across ap-* projects, both standalone and in the ap-base monorepo.

## Rationale

- **Isolation** - Never install project dependencies into the system Python
- **Reproducibility** - Everyone gets the same environment per `pyproject.toml`
- **Monorepo efficiency** - One venv for all submodules avoids redundant installs of shared dependencies (astropy, xisf, etc.)
- **Simplicity** - `make install-dev` is all you need; venv creation is automatic

## How It Works

Each submodule Makefile auto-detects whether it is inside the monorepo:

```makefile
VENV_DIR ?= $(if $(wildcard ../.venv/bin/python),../.venv,.venv)
PYTHON := $(VENV_DIR)/bin/python
```

`$(wildcard ../.venv/bin/python)` checks if a parent `.venv` exists. If it does (monorepo), `VENV_DIR` resolves to `../.venv`. Otherwise (standalone), it falls back to a local `.venv`. The `?=` still allows manual override via `make VENV_DIR=/some/path test`.

This means the same `cd submodule && make test` workflow works in both contexts with zero extra flags.

## Standalone Usage

When working on a single repo cloned independently:

```bash
cd ap-cull-light
make install-dev    # Creates .venv/, installs package + dev deps
make test           # Runs tests using .venv/bin/python
make default        # Runs all checks using .venv/bin/python
```

The venv is created automatically on first `make install-dev`. No manual `python -m venv` needed.

## Monorepo Usage (ap-base)

### One-time setup

Create the shared venv at the ap-base root:

```bash
cd ap-base
python3 -m venv .venv
```

### Installing submodules

cd into each submodule and run `make install-dev` as usual. The Makefile auto-detects `../.venv` and installs there:

```bash
cd ap-common
make install-dev        # Detects ../.venv, installs ap-common there

cd ../ap-cull-light
make install-dev        # Same shared venv, ap-common already available
```

All submodules share `ap-base/.venv/`. Each `make install-dev` adds that submodule's package and dev dependencies to the shared venv. Since all installs are editable (`pip install -e`), source changes in any submodule are immediately visible to all others.

### Day-to-day development

Work exactly the way you already do - cd into a submodule and run make:

```bash
cd ap-base/ap-cull-light
make test               # Uses ../.venv automatically
make default            # Full check suite, same shared venv
```

### Cross-repo development

When modifying ap-common and testing the change in ap-cull-light:

```bash
cd ap-base/ap-common
# Edit ap_common/constants.py
cd ../ap-cull-light
make test               # Picks up ap-common changes immediately
```

No `install-no-deps` workarounds needed - editable installs in a shared venv handle this naturally.

## Makefile Pattern

The full pattern used in [templates/Makefile](templates/Makefile):

```makefile
# Use parent .venv if it exists (monorepo), otherwise local .venv
VENV_DIR ?= $(if $(wildcard ../.venv/bin/python),../.venv,.venv)
PYTHON := $(VENV_DIR)/bin/python

$(VENV_DIR)/bin/python:
	python3 -m venv $(VENV_DIR)

install-dev: $(VENV_DIR)/bin/python
	$(PYTHON) -m pip install -e ".[dev]"
```

Key details:

- **Auto-detection**: `$(wildcard ../.venv/bin/python)` is evaluated at Makefile parse time. If the file exists, the `$(if)` returns `../.venv`; otherwise `.venv`.
- **Venv creation**: The `$(VENV_DIR)/bin/python` target only fires if the file does not exist. In the monorepo case, the shared venv already exists so this is a no-op.
- **Override**: `VENV_DIR ?=` means you can always force a specific path: `make VENV_DIR=.venv test` to use a local venv even inside the monorepo.

## CI Compatibility

GitHub Actions workflows do not need changes. The `actions/setup-python` action puts a specific Python version on `PATH`. When the Makefile runs `python3 -m venv`, it uses that version. In CI each repo is checked out standalone (no parent `.venv`), so the auto-detection falls through to a local `.venv`.

## What to Avoid

- **Do not activate the venv in Makefiles** - Use `$(VENV_DIR)/bin/python` directly. Shell `source activate` does not persist across Make recipe lines.
- **Do not use `VIRTUAL_ENV` environment variable** to detect venvs. Use the `VENV_DIR` Makefile variable for explicit control.
- **Do not install into system Python** - The Makefile template always installs into a venv.
- **Do not create submodule venvs manually** - Let `make install-dev` handle it. Only create the monorepo root venv manually (`python3 -m venv .venv` in ap-base).
