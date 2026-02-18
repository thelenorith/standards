# ap-common Usage

All ap-* projects must use constants and utilities from `ap-common` rather than redefining them locally.

## Rationale

- **Consistency** - All projects use identical constant names, not just values
- **Zero cognitive load** - Switching between projects requires no mental mapping
- **Maintainability** - Changes propagate automatically when ap-common is updated
- **Discoverability** - Single source of truth for all shared definitions

## Required Dependency

Every ap-* project (except ap-common itself) must include ap-common as a dependency:

```toml
# pyproject.toml
[project]
dependencies = [
    "ap-common",
]
```

## Available Constants

All shared constants are defined in [`ap_common/constants.py`](https://github.com/jewzaam/ap-common/blob/devel/ap_common/constants.py) and exported via `ap_common/__init__.py`.

Categories include:
- FITS header keys (`HEADER_*`)
- Normalized header names (`NORMALIZED_HEADER_*`)
- Image type constants (`TYPE_*`)
- Calibration type lists (`CALIBRATION_TYPES`, etc.)
- File extensions and patterns (`FILE_EXTENSION_*`, `DEFAULT_*_PATTERN`)
- Directory constants (`DIRECTORY_*`)

## Usage

Import constants directly from `ap_common`:

```python
from ap_common import HEADER_IMAGETYP, TYPE_LIGHT, CALIBRATION_TYPES

if headers[HEADER_IMAGETYP] == TYPE_LIGHT:
    process_light_frame(file)
elif headers[HEADER_IMAGETYP] in CALIBRATION_TYPES:
    process_calibration_frame(file)
```

## Anti-patterns

Do not do this:

```python
# BAD: Redefining constants locally
IMAGETYP = "IMAGETYP"
LIGHT_TYPE = "LIGHT"

# BAD: Aliasing to a different name
from ap_common import HEADER_IMAGETYP
IMAGE_TYPE_KEY = HEADER_IMAGETYP  # Don't do this

# BAD: Using string literals directly
if headers["IMAGETYP"] == "LIGHT":
    ...
```

Use constants directly with their original names:

```python
# GOOD: Import and use directly
from ap_common import HEADER_IMAGETYP, TYPE_LIGHT

if headers[HEADER_IMAGETYP] == TYPE_LIGHT:
    ...
```

The constant name `HEADER_IMAGETYP` is the same in every project. No aliases, no mappings, no project-specific names.

## Adding New Constants

When a new constant is needed across multiple projects:

1. Add it to `ap_common/constants.py`
2. Export it in `ap_common/__init__.py`
3. Update all projects to import from ap-common
4. Remove any local definitions
