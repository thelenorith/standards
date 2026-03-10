# Shared Virtual Environment

Standard for using Python virtual environments across related projects.

## Rationale

- **Isolation** - Never install project dependencies into the system Python
- **Reproducibility** - Everyone gets the same environment per `pyproject.toml`
- **Shared across repos** - One venv per project group avoids redundant installs of shared dependencies
- **Simplicity** - `make install-dev` is all you need; venv creation is automatic

## How It Works

Related projects sharing a group prefix (e.g., `dp-common`, `dp-cull-record`) share a single venv at `~/.venv/<group>/` (e.g., `~/.venv/dp/`). This location is:

- **Independent of directory structure** - works from any checkout, monorepo or standalone
- **In the home directory** - a natural place for user-level development tooling
- **Per project group** - multiple project families each get their own isolated venv

Each Makefile auto-detects whether the shared venv exists, with platform-appropriate paths:

```makefile
# Normalize HOME to forward slashes (no-op on Unix, fixes Windows backslashes)
HOME_DIR := $(subst \,/,$(HOME))

ifeq ($(OS),Windows_NT)
    VENV_DIR ?= $(if $(wildcard $(HOME_DIR)/.venv/<group>/Scripts/python.exe),$(HOME_DIR)/.venv/<group>,.venv)
    PYTHON := $(VENV_DIR)/Scripts/python.exe
else
    VENV_DIR ?= $(if $(wildcard $(HOME_DIR)/.venv/<group>/bin/python),$(HOME_DIR)/.venv/<group>,.venv)
    PYTHON := $(VENV_DIR)/bin/python
endif
```

`$(HOME)` is normalized to forward slashes via `$(subst \,/,$(HOME))` because on Windows `$(HOME)` contains backslashes (e.g. `C:\Users\you`) which the shell interprets as escape characters. Tilde is not used because Make does not expand it in variable assignments. `$(OS)` is set to `Windows_NT` by Windows itself, so the conditional works without any configuration.

- If the shared venv python exists: `VENV_DIR` resolves to `~/.venv/<group>`
- If it does not exist: `VENV_DIR` falls back to `.venv` (local)
- Manual override always works: `make VENV_DIR=.venv test`

## One-Time Setup

Create the shared venv once per project group:

```bash
python3 -m venv ~/.venv/dp
```

Then install projects into it from any checkout:

```bash
cd dp-common
make install-dev        # Detects ~/.venv/dp, installs there

cd ../dp-cull-record
make install-dev        # Same shared venv, dp-common already available
```

All installs are editable (`pip install -e`), so source changes in any submodule are immediately visible to all others.

Multiple project groups each get their own venv:

```bash
python3 -m venv ~/.venv/dp      # Data pipeline projects
python3 -m venv ~/.venv/web     # Web service projects
```

## Day-to-Day Development

Once `~/.venv/<group>` exists, every `make` command uses it automatically:

```bash
cd dp-cull-record
make test               # Uses ~/.venv/dp/bin/python
make default            # Full check suite, same shared venv
```

This works identically whether the repo is cloned standalone or checked out as a monorepo submodule.

### Cross-repo development

When modifying the common library and testing the change in another project:

```bash
cd dp-common
# Edit dp_common/constants.py
cd ../dp-cull-record
make test               # Picks up dp-common changes immediately
```

No `install-no-deps` workarounds needed - editable installs in a shared venv handle this naturally.

## Fallback to Local Venv

If `~/.venv/<group>` does not exist (new machine, CI, contributor who has not set it up), the Makefile falls back to a local `.venv` in the project directory:

```bash
cd dp-cull-record
make install-dev        # No ~/.venv/dp found, creates ./dp-cull-record/.venv/
make test               # Uses .venv/bin/python
```

This keeps everything working out of the box with no manual setup required.

## Makefile Pattern

The full pattern used in [templates/Makefile](templates/Makefile):

```makefile
# Normalize HOME to forward slashes (no-op on Unix, fixes Windows backslashes)
HOME_DIR := $(subst \,/,$(HOME))

# Use shared ~/.venv/<group> if it exists, otherwise local .venv
ifeq ($(OS),Windows_NT)
    VENV_DIR ?= $(if $(wildcard $(HOME_DIR)/.venv/<group>/Scripts/python.exe),$(HOME_DIR)/.venv/<group>,.venv)
    PYTHON := $(VENV_DIR)/Scripts/python.exe
else
    VENV_DIR ?= $(if $(wildcard $(HOME_DIR)/.venv/<group>/bin/python),$(HOME_DIR)/.venv/<group>,.venv)
    PYTHON := $(VENV_DIR)/bin/python
endif

$(info venv: $(VENV_DIR))

$(PYTHON):
	python3 -m venv $(VENV_DIR)

install-dev: $(PYTHON)
	$(PYTHON) -m pip install -e ".[dev]"
```

Key details:

- **Auto-detection**: The `$(wildcard)` check is evaluated at Makefile parse time. If the shared venv python exists, `VENV_DIR` resolves to the shared venv.
- **Windows support**: `$(OS)` is set to `Windows_NT` by Windows itself; venv layout uses `Scripts/python.exe` instead of `bin/python`.
- **Venv indicator**: `$(info venv: $(VENV_DIR))` prints which venv is in use on every Make invocation, so you always know at a glance whether you are using the shared or local venv.
- **Venv creation**: The `$(PYTHON)` target only fires if the file does not exist. When using the shared venv, this is a no-op.
- **Override**: `VENV_DIR ?=` means you can always force a specific path: `make VENV_DIR=.venv test` to use a local venv instead.

## CI Compatibility

GitHub Actions workflows do not need changes. In CI there is no `~/.venv/<group>`, so the auto-detection falls through to a local `.venv`. The `actions/setup-python` action puts a specific Python version on `PATH`, and `python3 -m venv` uses that version.

## What to Avoid

- **Do not activate the venv in Makefiles** - Use `$(VENV_DIR)/bin/python` directly. Shell `source activate` does not persist across Make recipe lines.
- **Do not use `VIRTUAL_ENV` environment variable** to detect venvs. Use the `VENV_DIR` Makefile variable for explicit control.
- **Do not install into system Python** - The Makefile template always installs into a venv.
- **Do not use `~` in Makefiles** - Use `$(HOME)`. Make does not expand tilde in variable assignments.
- **Do not use `$(HOME)` directly in paths** - Use `$(subst \,/,$(HOME))` to normalize backslashes. On Windows, `$(HOME)` contains backslashes that the shell interprets as escape characters.
