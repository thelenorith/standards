# Common Library Usage

When a project group has a shared common library, all projects in that group must use its constants and utilities rather than redefining them locally. If no shared library exists, local definitions are expected.

## Rationale

- **Consistency** - All projects use identical constant names, not just values
- **Zero cognitive load** - Switching between projects requires no mental mapping
- **Maintainability** - Changes propagate automatically when the common library is updated
- **Discoverability** - Single source of truth for all shared definitions

## Required Dependency

When a common library exists, every project in the group (except the common library itself) must include it as a dependency:

```toml
# pyproject.toml
[project]
dependencies = [
    "common",
]
```

## Available Constants

All shared constants are defined in the common library's `constants.py` module and exported via `__init__.py`.

Organize constants by category using descriptive prefixes:
- Configuration keys (`CONFIG_*`)
- Status constants (`STATUS_*`)
- Type constants (`TYPE_*`)
- File extensions and patterns (`FILE_EXTENSION_*`, `DEFAULT_*_PATTERN`)
- Directory constants (`DIRECTORY_*`)

## Usage

Import constants directly from the common library:

```python
from common import STATUS_ACTIVE, TYPE_PRIMARY, DEFAULT_PATTERN

if record[STATUS_ACTIVE]:
    process_primary(record)
```

## Anti-patterns

Do not do this:

```python
# BAD: Redefining constants locally
STATUS = "active"
PRIMARY_TYPE = "primary"

# BAD: Aliasing to a different name
from common import STATUS_ACTIVE
MY_STATUS = STATUS_ACTIVE  # Don't do this

# BAD: Using string literals directly
if record["active"]:
    ...
```

Use constants directly with their original names:

```python
# GOOD: Import and use directly
from common import STATUS_ACTIVE, TYPE_PRIMARY

if record[STATUS_ACTIVE]:
    ...
```

The constant name is the same in every project. No aliases, no mappings, no project-specific names.

## Adding New Constants

When a new constant is needed across multiple projects:

1. Add it to the common library's `constants.py`
2. Export it in `__init__.py`
3. Update all projects to import from the common library
4. Remove any local definitions
