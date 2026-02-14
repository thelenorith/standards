# GitHub Workflows

Standard CI workflows for ap-* projects.

## Required Workflows

| Workflow | Template | Description |
|----------|----------|-------------|
| Test | [test.yml](templates/workflows/test.yml) | Run pytest on Python 3.10-3.14 |
| Lint | [lint.yml](templates/workflows/lint.yml) | Run flake8 linter |
| Typecheck | [typecheck.yml](templates/workflows/typecheck.yml) | Run mypy type checker |
| Format Check | [format.yml](templates/workflows/format.yml) | Verify black formatting |
| Coverage | [coverage.yml](templates/workflows/coverage.yml) | Enforce 80% coverage threshold |

## Setup

Copy all files from [templates/workflows/](templates/workflows/) to your project's `.github/workflows/` directory:

```bash
cp -r standards/templates/workflows/* .github/workflows/
```

No modifications needed - workflows use Makefile targets which handle project-specific paths.

## Conventions

### Python versions

Test on Python 3.10 through 3.14. Use 3.12 for single-version jobs (lint, format, typecheck, coverage).

### Actions versions

Use current major versions:
- `actions/checkout@v4`
- `actions/setup-python@v5`

### Triggers

All workflows run on push to main and all PRs to main:

```yaml
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
```

### Use Makefile targets

Workflows call Makefile targets, not duplicate commands:

```yaml
- name: Run tests
  run: make test
```

This keeps CI configuration simple and ensures local `make test` matches CI behavior.
