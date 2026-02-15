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

## Monorepo Development

The recommended approach is to use a shared venv at the ap-base root. See [Shared Virtual Environment](shared-venv.md) for the full standard.

```bash
cd ap-base
make install-all    # Creates .venv/, installs all submodules editable
```

All submodules share `ap-base/.venv/`. Editable installs mean changes to any submodule source (e.g., ap-common) are immediately visible to all others. No `install-no-deps` workarounds needed.

To run checks in a single submodule:

```bash
make -C ap-cull-light VENV_DIR=$(pwd)/.venv default
```

The `install-no-deps` target is still available for cases where you need to install a package without pulling its dependencies from the network.

## Template

Copy [templates/Makefile](templates/Makefile) to your project and replace `<name>` with your project name.

## Conventions

### VENV_DIR variable

The venv directory is configurable via `VENV_DIR`. Use `?=` so the monorepo can override it:

```makefile
VENV_DIR ?= .venv
```

When standalone, this defaults to `.venv` in the project directory. When called from ap-base, the monorepo passes `VENV_DIR=$(CURDIR)/.venv` so all submodules share one venv.

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
