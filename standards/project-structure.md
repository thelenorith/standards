# Project Structure

Standard directory layout for ap-* Python projects.

## Directory Layout

```
ap-<name>/
├── .venv/                  # Virtual environment (created by make, git-ignored)
├── ap_<name>/              # Package directory (underscores)
│   ├── __init__.py
│   ├── __main__.py         # Entry point for python -m
│   └── <module>.py
├── tests/
│   ├── __init__.py
│   └── test_<module>.py
├── .github/
│   └── workflows/
│       ├── test.yml
│       ├── lint.yml
│       ├── typecheck.yml
│       ├── format.yml
│       └── coverage.yml
├── .gitignore
├── LICENSE
├── MANIFEST.in
├── Makefile
├── README.md
├── TEST_PLAN.md
└── pyproject.toml
```

The `.venv/` directory is created automatically by `make install-dev` and must be git-ignored. When working in the ap-base monorepo, submodules share a single venv at the monorepo root instead. See [Shared Virtual Environment](shared-venv.md).

## Required Files

| File | Purpose |
|------|---------|
| `LICENSE` | Project license |
| `README.md` | Project documentation |
| `TEST_PLAN.md` | Testing strategy and rationale (see [template](templates/TEST_PLAN.md)) |
| `MANIFEST.in` | sdist inclusion rules |
| `Makefile` | Build/test automation |
| `pyproject.toml` | Package configuration |
| `.gitignore` | Git ignore patterns |

## Naming Conventions

See [Naming](naming.md) for the full naming taxonomy and pattern.

- **Repository**: `ap-{verb}-{noun}` or `ap-{verb}-{noun}-to-{dest}` (hyphenated)
- **Package directory**: Same as repository with underscores (e.g., `ap_cull_light`)
- **Module files**: lowercase, underscored
- **Test files**: `test_<module>.py`

## pyproject.toml

```toml
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "ap-<name>"
version = "0.1.0"
description = "<brief description>"
readme = "README.md"
requires-python = ">=3.10"
license = {file = "LICENSE"}
authors = [
    {name = "Naveen Malik"}
]
keywords = ["astrophotography"]
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Science/Research",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Programming Language :: Python :: 3.13",
    "Programming Language :: Python :: 3.14",
]
dependencies = []

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "pytest-cov>=4.0",
    "pytest-mock>=3.0",
    "black>=23.0",
    "flake8>=6.0",
    "mypy==1.11.2",
]

[tool.setuptools.packages.find]
where = ["."]
include = ["ap_<name>*"]
```

## .gitignore

```gitignore
# Python
__pycache__/
*.py[cod]
*.egg-info/
dist/
build/
.eggs/

# Testing
.pytest_cache/
.coverage
htmlcov/

# IDE
.vscode/
.idea/

# Virtual environments
venv/
.venv/

# Claude Code local settings
.claude/settings.local.json
```

## MANIFEST.in

```
include LICENSE
include README.md
recursive-include ap_<name> *.py
```
