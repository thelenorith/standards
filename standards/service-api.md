# Service API Standards

Conventions for defining programmatic service interfaces in ap-* tools.

## Purpose

Each tool exposes its functionality through two supported interfaces:

| Interface | Consumer | Defined By |
|-----------|----------|------------|
| CLI | Users, scripts, automation | `argparse` in `main()` |
| Service API | UI, other programs | Service module functions |

The service API provides programmatic access to tool functionality without requiring module imports of internal implementation. Services are the **only** supported programmatic interface — callers must not import implementation modules directly.

## Architecture

```
┌─────────────┐     ┌─────────────────┐     ┌────────────────────┐
│   CLI        │────▶│  Service API     │────▶│  Implementation    │
│  (argparse)  │     │  (public contract)│    │  (internal)        │
└─────────────┘     └─────────────────┘     └────────────────────┘
       ▲                     ▲
       │                     │
     Users               UI / Programs
```

- **CLI layer** — Parses arguments, calls service functions. Thin adapter.
- **Service layer** — Public API contract. Stable signatures. The boundary that callers depend on.
- **Implementation** — Internal logic. Free to change without notice.

## Why Services (Not Direct Imports)

| Concern | Direct Import | Service API |
|---------|---------------|-------------|
| Coupling | Caller depends on internal structure | Caller depends on stable contract |
| Versioning | Any internal rename breaks callers | Only service signature changes matter |
| Maintainability | Refactoring ripples to all consumers | Refactoring stays internal |
| Testability | Must mock internals | Mock service boundary |

Direct imports of implementation modules are **not supported**. Internal module structure, function names, and signatures may change without notice.

## Module Structure

Service APIs live in a dedicated module per project:

```
ap_<name>/
├── __init__.py
├── service.py          # Public service API
├── <implementation>.py # Internal modules (not for external use)
└── ...
```

The `service.py` module is the sole public programmatic interface. All other modules are internal.

## Service Function Conventions

### Signatures

Service functions follow [Python Style Standards](python-style.md) — keyword-only arguments for all optional parameters:

```python
# service.py

def process_directory(
    source_dir: str,
    dest_dir: str,
    *,
    dry_run: bool = False,
    quiet: bool = False,
    debug: bool = False,
    no_overwrite: bool = True,
) -> ProcessResult:
    """Process all frames in source_dir and output to dest_dir."""
    ...
```

| Rule | Rationale |
|------|-----------|
| Required parameters before `*` | Positional-friendly for simple calls |
| Optional parameters after `*` | Enforces named usage, prevents positional bugs |
| Type annotations on all parameters | Callers know the contract without reading source |
| Return type annotation | Callers know what to expect |

### Parameter Naming

Service function parameters must match CLI option names (minus the `--` prefix, with hyphens converted to underscores):

| CLI Option | Service Parameter |
|------------|-------------------|
| `--dryrun` | `dryrun` |
| `--no-overwrite` | `no_overwrite` |
| `--blink-dir` | `blink_dir` |
| `--debug` | `debug` |
| `--quiet` | `quiet` |

This 1:1 mapping keeps the CLI layer thin — it passes parsed arguments directly to the service with no translation.

### Required Parameters

All service functions that perform actions must accept these optional parameters:

| Parameter | Type | Default | Purpose |
|-----------|------|---------|---------|
| `dry_run` | `bool` | `False` | Perform dry run without side effects |
| `quiet` | `bool` | `False` | Suppress non-essential output |
| `debug` | `bool` | `False` | Enable debug output |

## Return Types

Service functions return structured result objects, not exit codes.

### Result Pattern

Define a result dataclass per operation:

```python
from dataclasses import dataclass

@dataclass
class ProcessResult:
    processed_count: int
    skipped_count: int
    error_count: int
    errors: list[str]
```

| Rule | Rationale |
|------|-----------|
| Return dataclass, not dict | Type-checked, documented fields |
| Return dataclass, not tuple | Named access, not positional |
| Include counts and details | Caller decides how to present results |
| No print/log in return values | Results are data, not formatted output |

### CLI Translates Results to Output

The CLI layer is responsible for translating service results into user-facing output:

```python
# main.py (CLI layer)
def main():
    args = parse_args()
    logger = setup_logging(name="ap_my_tool", debug=args.debug, quiet=args.quiet)

    result = service.process_directory(
        args.source,
        args.dest,
        dry_run=args.dryrun,
        quiet=args.quiet,
        debug=args.debug,
    )

    if not args.quiet:
        print(f"Processed {result.processed_count} files")

    if result.error_count > 0:
        for error in result.errors:
            logger.error(error)
        sys.exit(EXIT_ERROR)

    sys.exit(EXIT_SUCCESS)
```

The service function itself does **not** call `sys.exit()`, print summaries, or format output for humans.

## Error Handling

### Services Raise Exceptions

Service functions signal errors by raising exceptions, not by returning error codes or calling `sys.exit()`.

| Error Type | Mechanism |
|------------|-----------|
| Invalid arguments | Raise `ValueError` |
| Missing files/resources | Raise `FileNotFoundError` |
| Operational failures | Return in result (e.g., `error_count`, `errors` list) |
| Fatal/unrecoverable | Raise appropriate exception |

**Distinction:** Errors that prevent the operation from starting are exceptions. Errors encountered while processing items are collected in the result.

```python
# service.py
def process_directory(
    source_dir: str,
    dest_dir: str,
    *,
    dry_run: bool = False,
) -> ProcessResult:
    if not os.path.isdir(source_dir):
        raise FileNotFoundError(f"Source directory not found: {source_dir}")

    errors = []
    processed = 0
    for item in get_items(source_dir):
        try:
            process_item(item, dest_dir, dry_run=dry_run)
            processed += 1
        except Exception as e:
            errors.append(f"{item}: {e}")

    return ProcessResult(
        processed_count=processed,
        skipped_count=0,
        error_count=len(errors),
        errors=errors,
    )
```

### CLI Translates Exceptions to Exit Codes

```python
# main.py
def main():
    args = parse_args()
    try:
        result = service.process_directory(args.source, args.dest, dry_run=args.dryrun)
    except FileNotFoundError as e:
        logger.error(str(e))
        sys.exit(EXIT_ERROR)
    except ValueError as e:
        logger.error(str(e))
        sys.exit(EXIT_ERROR)
```

## What Services Must NOT Do

| Anti-Pattern | Why | Correct Approach |
|--------------|-----|------------------|
| Call `sys.exit()` | Kills the calling process | Raise exception or return result |
| Print to stdout/stderr | Output is the caller's responsibility | Return data in result object |
| Parse CLI arguments | That is the CLI layer's job | Accept parameters directly |
| Read environment variables | Implicit coupling | Accept values as parameters |
| Configure logging | Entry point responsibility | Use existing logger via `logging.getLogger()` |

## What Services Must Do

| Requirement | Rationale |
|-------------|-----------|
| Validate inputs | Fail fast with clear exceptions |
| Return structured results | Callers need data, not formatted strings |
| Honor `dry_run` | No side effects when dry_run is True |
| Be independently testable | No CLI or UI dependencies |

## Testing Services

Service functions are tested directly — no `sys.argv` patching needed (see [CLI Testing](cli-testing.md) for testing the CLI layer).

```python
def test_process_directory_returns_count(tmp_path):
    source = tmp_path / "source"
    source.mkdir()
    create_test_files(source, count=3)
    dest = tmp_path / "dest"
    dest.mkdir()

    result = service.process_directory(str(source), str(dest))

    assert result.processed_count == 3
    assert result.error_count == 0


def test_process_directory_missing_source_raises():
    with pytest.raises(FileNotFoundError):
        service.process_directory("/nonexistent", "/dest")


def test_process_directory_dryrun_no_side_effects(tmp_path):
    source = tmp_path / "source"
    source.mkdir()
    create_test_files(source, count=3)
    dest = tmp_path / "dest"
    dest.mkdir()

    result = service.process_directory(str(source), str(dest), dry_run=True)

    assert result.processed_count == 3
    assert len(list(dest.iterdir())) == 0  # Nothing actually written
```

## Anti-Patterns

| Anti-Pattern | Problem | Correct Approach |
|--------------|---------|------------------|
| Importing implementation modules directly | Breaks when internals change | Import from `service.py` only |
| Returning raw dicts from services | No type safety, no documentation | Use dataclasses |
| Mixing service logic with CLI parsing | Untestable without `sys.argv` mocking | Separate layers |
| Service functions that print results | Output format is caller's choice | Return data |
| Catching all exceptions silently | Hides bugs | Let unexpected exceptions propagate |
| `sys.exit()` in service code | Cannot be used programmatically | Raise exceptions |
