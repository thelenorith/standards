# Makefile Standards

Standard Makefile targets for ap-* Python projects.

## Default Target

Running `make` without specifying a target runs the `default` target, which executes all validation steps (format, lint, typecheck, test, coverage). This ensures code quality checks are easy to run.

```bash
make           # Runs default target (all validations)
make default   # Same as above (explicit)
```

## Required Targets

| Target | Description |
|--------|-------------|
| `default` | Run format, lint, typecheck, test, coverage |
| `install` | Install package |
| `install-dev` | Install in editable mode with dev deps |
| `install-no-deps` | Install in editable mode without dependencies |
| `uninstall` | Uninstall package |
| `clean` | Remove build artifacts |
| `format` | Format code with black |
| `lint` | Lint with flake8 |
| `typecheck` | Type check with mypy |
| `test` | Run pytest |
| `coverage` | Run pytest with coverage |

## Shared Venv

All ap-* projects share a single venv at `~/.venv/ap/`. See [Shared Virtual Environment](shared-venv.md) for the full standard.

One-time setup:

```bash
python3 -m venv ~/.venv/ap
```

Then cd into any repo and run make as usual:

```bash
cd ap-common
make install-dev        # Detects ~/.venv/ap, installs there

cd ../ap-cull-light
make install-dev        # Same shared venv
make test               # Uses ~/.venv/ap automatically
```

The auto-detection uses `$(wildcard $(HOME)/.venv/ap/bin/python)` in each Makefile. If the shared venv does not exist (CI, new machine), it falls back to a local `.venv`.

The `install-no-deps` target is still available for cases where you need to install a package without pulling its dependencies from the network.

## Template

Copy [templates/Makefile](templates/Makefile) to your project and replace `<name>` with your project name.

## Conventions

### VENV_DIR variable

`VENV_DIR` auto-detects the shared venv at `~/.venv/ap` or falls back to a local one:

```makefile
VENV_DIR ?= $(if $(wildcard $(HOME)/.venv/ap/bin/python),$(HOME)/.venv/ap,.venv)
```

- **Shared venv exists**: `VENV_DIR` resolves to `~/.venv/ap`
- **No shared venv**: `VENV_DIR` resolves to `.venv` (local)
- **Override**: `make VENV_DIR=.venv test` always works

See [Shared Virtual Environment](shared-venv.md) for full details.

### PYTHON variable

`PYTHON` points to the venv's Python binary. Do not hardcode `python` or `python3` in targets:

```makefile
PYTHON := $(VENV_DIR)/bin/python
```

### Venv creation target

The venv is created automatically as a Make prerequisite. Make only runs this if the file does not exist:

```makefile
$(VENV_DIR)/bin/python:
	python3 -m venv $(VENV_DIR)
```

### Dependencies

Targets that need the package installed should depend on `install-dev`, which itself depends on the venv existing:

```makefile
install-dev: $(VENV_DIR)/bin/python
	$(PYTHON) -m pip install -e ".[dev]"

format: install-dev
	$(PYTHON) -m black ap_<name> tests
```

### Quiet failures in clean

Use `|| true` for commands that might fail during cleanup:

```makefile
find . -type d -name __pycache__ -exec rm -r {} + 2>/dev/null || true
```

### Line length

Match black's default of 88 characters:

```makefile
--max-line-length=88
```

## What to Avoid

- Complex shell logic
- Platform-specific commands without fallbacks
- Hardcoded paths
- Targets that modify git state
