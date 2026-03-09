# Logging, Progress, and Output Standards

Guidelines for output methods in Python CLI tools. Based on industry best practices including the 12-Factor App methodology and Python logging conventions.

## Overview

| Output Method | Purpose | Stream | When to Use |
|---------------|---------|--------|-------------|
| Logging | Operational/diagnostic | stderr | Debug info, warnings, errors |
| Progress | User feedback | stderr | Long-running operations |
| Print | Program output | stdout | Results, summaries, piped data |

## Logging

### When to Use Logging

Use Python logging for **operational and diagnostic information**:

| Log Level | Use For |
|-----------|---------|
| `DEBUG` | Detailed diagnostic info, variable values, execution flow |
| `INFO` | Normal operational messages, milestones |
| `WARNING` | Unexpected situations that don't prevent operation |
| `ERROR` | Failures that prevent completing a specific operation |
| `CRITICAL` | Severe errors that prevent program continuation |

### Configuration

Use a centralized logging setup for consistent configuration:

```python
from common import setup_logging

def main():
    logger = setup_logging(name="my_tool", debug=args.debug, quiet=args.quiet)
```

| Rule | Rationale |
|------|-----------|
| Configure once at entry point | Prevents duplicate handlers |
| Use tool-specific logger name | Enables filtering by source |
| Control level via `--debug` and `--quiet` flags | User controls verbosity |

### Logging Level Behavior

| Flags | Effective Level | Output |
|-------|-----------------|--------|
| Default | INFO | INFO, WARNING, ERROR, CRITICAL |
| `--quiet` | WARNING | WARNING, ERROR, CRITICAL only |
| `--debug` | DEBUG | DEBUG, INFO, WARNING, ERROR, CRITICAL |
| `--debug --quiet` | DEBUG | DEBUG, INFO, WARNING, ERROR, CRITICAL (debug overrides quiet) |

### Logger Naming

Use hierarchical names for filtering:

```python
# Main module
logger = setup_logging(name="my_tool", debug=debug)

# Submodules
logger = logging.getLogger("my_tool.submodule")
```

### What to Log

```python
# DEBUG: Detailed diagnostic information
logger.debug(f"Processing file: {filename}")
logger.debug(f"Header values: {headers}")

# INFO: Operational milestones
logger.info("Starting processing")
logger.info(f"Found {count} files to process")

# INFO: Multi-parameter information (single statement, key=value format)
logger.info(
    f"Executing command: binary={binary}, script={script}, "
    f"log={log_file}, instance={instance_id}"
)

# WARNING: Recoverable issues
logger.warning(f"Missing optional key: {key}")
logger.warning(f"File exists, skipping: {dest}")

# ERROR: Operation failures
logger.error(f"Failed to read file: {filename}")
logger.error(f"Invalid format in {path}")
```

### What NOT to Log

| Avoid | Use Instead |
|-------|-------------|
| User-facing summaries | Print to stdout |
| Progress updates | Progress indicators |
| Primary program output | Print to stdout |

**Anti-Pattern: Multiple log calls with whitespace padding**

```python
# BAD: Multiple separate log calls with whitespace padding
logger.info("Executing command...")
logger.info(f"  Binary: {binary}")
logger.info(f"  Script: {script}")
logger.info(f"  Log: {log_file}")

# GOOD: Single log statement with key=value format
logger.info(
    f"Executing command: binary={binary}, script={script}, log={log_file}"
)
```

## Progress Indicators

### When to Use Progress

Use progress indicators for **long-running operations** that process multiple items:

| Scenario | Progress Type |
|----------|--------------|
| Processing known file list | `progress_iter()` |
| Dynamic status updates needed | `ProgressTracker` |
| Unknown total count | `ProgressTracker` (manual mode) |
| < 3 items or instant operations | None needed |

### Using Common Progress Utilities

**Simple iteration:**

```python
from common import progress_iter

for f in progress_iter(files, desc="Processing", enabled=not quiet):
    process_file(f)
```

**With status updates:**

```python
from common import ProgressTracker

with ProgressTracker(files, desc="Processing", enabled=show_progress) as tracker:
    for f in tracker:
        tracker.set_status(os.path.basename(f))
        process_file(f)
```

**Unknown total:**

```python
tracker = ProgressTracker(desc="Scanning", enabled=show_progress)
tracker.start()
for item in generator():
    tracker.update(status=item.name)
tracker.finish()
```

### Progress Configuration

| Parameter | Purpose |
|-----------|---------|
| `desc` | Action being performed (e.g., "Moving files") |
| `unit` | What's being counted (e.g., "files", "dirs") |
| `enabled` | Control via CLI flag (default: True) |

### Controlling Progress Display

Progress should be controllable via CLI:

| Flag | Effect on Progress |
|------|-------------------|
| `--quiet` / `-q` | Suppress progress indicators |
| Default (no flag) | Show progress indicators |

Note: The `--quiet` flag also suppresses INFO-level logging and summary statistics. See [CLI Standards](cli.md#--quiet-flag-behavior) for full specification.

```python
parser.add_argument("--quiet", "-q", action="store_true",
                    help="suppress non-essential output")
```

### What NOT to Use for Progress

| Avoid | Why |
|-------|-----|
| Manual dot printing (`print(".", end="")`) | Inconsistent, no metrics |
| Logging progress updates | Wrong abstraction level |
| Custom progress implementations | Duplicates common library functionality |

## Print Statements (stdout)

### When to Use Print

Use print for **primary program output** that may be piped or captured:

| Use Case | Example |
|----------|---------|
| Final results/summaries | "Moved 42 files to /data" |
| Data output | File lists, JSON output |
| User decisions | "REJECTED: file.dat (low quality)" |
| Dry-run output | "Would move: src -> dest" |

### Print Guidelines

```python
# Final summary (suppressed by --quiet)
if not quiet:
    print(f"Processed {count} files successfully")

# Dry-run output
if dryrun:
    print(f"Would move: {src} -> {dest}")

# Rejection/decision output
print(f"REJECTED: {filename} (reason: {reason})")
```

### What NOT to Print

| Avoid | Use Instead |
|-------|-------------|
| Debug information | `logger.debug()` |
| Operational status | `logger.info()` |
| Warnings | `logger.warning()` |
| Progress dots | `progress_iter()` |

## Decision Matrix

Use this matrix to choose the right output method:

| Question | Yes -> Use |
|----------|-----------|
| Is this diagnostic/debugging information? | Logging |
| Is this a warning or error condition? | Logging |
| Is this showing progress through a list? | Progress indicator |
| Is this the primary output/result? | Print |
| Should this appear in piped output? | Print |
| Is this dry-run information? | Print |

## Common Patterns

### Standard CLI Tool Structure

```python
from common import setup_logging, progress_iter

def main():
    args = parse_args()
    logger = setup_logging(name="my_tool", debug=args.debug, quiet=args.quiet)

    logger.info("Starting processing")  # Suppressed by --quiet

    results = []
    for f in progress_iter(files, desc="Processing", enabled=not args.quiet):
        logger.debug(f"Processing: {f}")
        result = process(f)
        if result:
            results.append(result)

    logger.info(f"Completed with {len(results)} results")  # Suppressed by --quiet

    # Summary output (suppressed by --quiet)
    if not args.quiet:
        print(f"Processed {len(results)} files")
```

### Dry-Run Pattern

```python
for src, dest in progress_iter(moves, desc="Moving files", enabled=not quiet):
    if dryrun:
        print(f"Would move: {src} -> {dest}")
    else:
        shutil.move(src, dest)
        logger.debug(f"Moved: {src} -> {dest}")

if not dryrun:
    print(f"Moved {len(moves)} files")
```

### Error Handling Pattern

```python
try:
    result = process_file(path)
except FileNotFoundError:
    logger.error(f"File not found: {path}")
    return None
except PermissionError:
    logger.error(f"Permission denied: {path}")
    return None
except Exception as e:
    logger.exception(f"Unexpected error processing {path}")
    raise
```

## Summary Table

| Output Type | Stream | Controlled By | Common Utility |
|-------------|--------|---------------|----------------|
| Logging (DEBUG) | stderr | `--debug` | `setup_logging()`, `get_logger()` |
| Logging (INFO) | stderr | `--quiet` (suppresses) | `setup_logging()`, `get_logger()` |
| Logging (WARNING+) | stderr | Always shown | `setup_logging()`, `get_logger()` |
| Progress | stderr | `--quiet` (suppresses) | `progress_iter()`, `ProgressTracker` |
| Summary output | stdout | `--quiet` (suppresses) | None (built-in) |
| Dry-run output | stdout | Always shown | None (built-in) |

## Required CLI Flags

Per [CLI Standards](cli.md), all tools must support these flags:

| Flag | Purpose |
|------|---------|
| `--debug` | Enable DEBUG-level logging |
| `--quiet` / `-q` | Suppress non-essential output (progress, INFO logs, summaries) |

See [CLI Standards - --quiet Flag Behavior](cli.md#--quiet-flag-behavior) for full specification.

## Anti-Patterns

| Anti-Pattern | Problem | Correct Approach |
|--------------|---------|------------------|
| `print("Processing...")` for status | Clutters stdout | Use logging or progress |
| `print(".", end="")` for progress | No metrics, inconsistent | Use `progress_iter()` |
| Logging final results | Results don't appear in piped output | Use print |
| Debug info to stdout | Breaks piped workflows | Use `logger.debug()` |
| Per-module logging setup | Duplicate handlers | Configure once at entry |
| Ignoring `--debug` flag | Users can't diagnose issues | Pass to `setup_logging()` |
| `if debug: logger.debug(...)` | Redundant conditional | Remove `if debug:` check, logger handles level filtering |
| Multiple log calls for one event | Hard to read, fragmented | Combine into single log statement |
| Whitespace padding in logs (`"  Binary: {x}"`) | Logs aren't structured output | Use key=value format without padding |
