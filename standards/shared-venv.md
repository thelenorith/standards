# Shared Virtual Environment

Standard for using Python virtual environments across ap-* projects.

## Rationale

- **Isolation** - Never install project dependencies into the system Python
- **Reproducibility** - Everyone gets the same environment per `pyproject.toml`
- **Shared across repos** - One venv for all ap-* tools avoids redundant installs of shared dependencies (astropy, xisf, etc.)
- **Simplicity** - `make install-dev` is all you need; venv creation is automatic

## How It Works

All ap-* projects share a single venv at `~/.venv/ap/`. This location is:

- **Independent of directory structure** - works from any checkout, monorepo or standalone
- **Uniquely named** - `ap` identifies it as the astrophotography pipeline venv, no collisions with other projects
- **In the home directory** - a natural place for user-level development tooling

Each submodule Makefile auto-detects whether the shared venv exists:

```makefile
VENV_DIR ?= $(if $(wildcard $(HOME)/.venv/ap/bin/python),$(HOME)/.venv/ap,.venv)
PYTHON := $(VENV_DIR)/bin/python
```

`$(HOME)` is used instead of `~` because Make does not expand tilde in variable assignments.

- If `~/.venv/ap/bin/python` exists: `VENV_DIR` resolves to `~/.venv/ap` (shared)
- If it does not exist: `VENV_DIR` falls back to `.venv` (local)
- Manual override always works: `make VENV_DIR=.venv test`

## One-Time Setup

Create the shared venv once:

```bash
python3 -m venv ~/.venv/ap
```

Then install submodules into it from any checkout:

```bash
cd ap-common
make install-dev        # Detects ~/.venv/ap, installs there

cd ../ap-cull-light
make install-dev        # Same shared venv, ap-common already available
```

All installs are editable (`pip install -e`), so source changes in any submodule are immediately visible to all others.

## Day-to-Day Development

Once `~/.venv/ap` exists, every `make` command uses it automatically:

```bash
cd ap-cull-light
make test               # Uses ~/.venv/ap/bin/python
make default            # Full check suite, same shared venv
```

This works identically whether the repo is cloned standalone or checked out as an ap-base submodule.

### Cross-repo development

When modifying ap-common and testing the change in ap-cull-light:

```bash
cd ap-common
# Edit ap_common/constants.py
cd ../ap-cull-light
make test               # Picks up ap-common changes immediately
```

No `install-no-deps` workarounds needed - editable installs in a shared venv handle this naturally.

## Fallback to Local Venv

If `~/.venv/ap` does not exist (new machine, CI, contributor who has not set it up), the Makefile falls back to a local `.venv` in the project directory:

```bash
cd ap-cull-light
make install-dev        # No ~/.venv/ap found, creates ./ap-cull-light/.venv/
make test               # Uses .venv/bin/python
```

This keeps everything working out of the box with no manual setup required.

## Makefile Pattern

The full pattern used in [templates/Makefile](templates/Makefile):

```makefile
# Use shared ~/.venv/ap if it exists, otherwise local .venv
VENV_DIR ?= $(if $(wildcard $(HOME)/.venv/ap/bin/python),$(HOME)/.venv/ap,.venv)
PYTHON := $(VENV_DIR)/bin/python

$(VENV_DIR)/bin/python:
	python3 -m venv $(VENV_DIR)

install-dev: $(VENV_DIR)/bin/python
	$(PYTHON) -m pip install -e ".[dev]"
```

Key details:

- **Auto-detection**: `$(wildcard $(HOME)/.venv/ap/bin/python)` is evaluated at Makefile parse time. If the file exists, `VENV_DIR` resolves to the shared venv.
- **Venv creation**: The `$(VENV_DIR)/bin/python` target only fires if the file does not exist. When using the shared venv, this is a no-op.
- **Override**: `VENV_DIR ?=` means you can always force a specific path: `make VENV_DIR=.venv test` to use a local venv instead.

## CI Compatibility

GitHub Actions workflows do not need changes. In CI there is no `~/.venv/ap`, so the auto-detection falls through to a local `.venv`. The `actions/setup-python` action puts a specific Python version on `PATH`, and `python3 -m venv` uses that version.

## What to Avoid

- **Do not activate the venv in Makefiles** - Use `$(VENV_DIR)/bin/python` directly. Shell `source activate` does not persist across Make recipe lines.
- **Do not use `VIRTUAL_ENV` environment variable** to detect venvs. Use the `VENV_DIR` Makefile variable for explicit control.
- **Do not install into system Python** - The Makefile template always installs into a venv.
- **Do not use `~` in Makefiles** - Use `$(HOME)`. Make does not expand tilde in variable assignments.
