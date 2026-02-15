# Python Style Standards

## Function Calls: Named Parameters

**Prefer explicit named parameters over positional parameters when calling functions.**

### Rule

When calling functions with multiple parameters, especially optional parameters, use named parameter assignment instead of relying on positional order.

### Rationale

Positional parameters are error-prone:
- Parameter order changes can silently break code
- Wrong values can be passed to wrong parameters with no type checking
- Code is harder to understand without reading function signature

### Example Bug

This bug actually occurred in production:

```python
# Function signature
def move_file(from_file: str, to_file: str, debug: bool = False, dryrun: bool = False):
    ...

# WRONG: dryrun passed as 3rd positional argument maps to debug parameter
move_file(src, dest, dry_run)  # dry_run → debug, dryrun stays False (default)
# Result: Files actually moved with debug output!

# CORRECT: Named parameter ensures correct mapping
move_file(src, dest, dryrun=dry_run)
```

### Guidelines

**Required positional parameters:** Can use positional or named
```python
# Both acceptable
check_calibration_status(image_dir, source_dir)
check_calibration_status(directory=image_dir, source_dir=source_dir)
```

**Optional parameters:** Must use named assignment
```python
# WRONG: Positional optional parameters
status = check_calibration_status(image_dir, source_dir, debug, scale_darks)

# CORRECT: Named optional parameters
status = check_calibration_status(
    image_dir,
    source_dir,
    debug=debug,
    scale_darks=scale_darks
)
```

**Boolean flags:** Always use named assignment
```python
# WRONG: Hard to understand what True/False mean
process_data(data, True, False, True)

# CORRECT: Clear intent
process_data(data, validate=True, strict=False, verbose=True)
```

### Exceptions

Positional parameters are acceptable when:
- Only 1-2 required parameters with clear, unambiguous meaning
- Very common functions where positional usage is idiomatic (e.g., `print()`, `len()`)
- All parameters are required (no defaults)

### Enforcement

- Code reviewers should flag positional optional parameters
- Consider adding linter rules (flake8-named-arguments plugin)
- Update existing code opportunistically when making changes

## Function Definitions: Keyword-Only Arguments (`*`)

**Use `*` in function signatures to enforce keyword-only arguments for optional parameters.**

### Rule

When defining functions with optional parameters (parameters with defaults), place a bare `*` before them to make them keyword-only. Required parameters go before the `*`, optional parameters go after.

### Rationale

The `*` syntax enforces at the language level what the "Named Parameters" guideline above recommends by convention. Callers **cannot** pass keyword-only arguments positionally — Python raises `TypeError` if they try. This eliminates the entire class of positional-argument bugs rather than relying on code review to catch them.

### Example

```python
def process_blink_directory(
    library_dir: Path,
    blink_dir: Path,
    date_dir_pattern: str,
    *,
    dry_run: bool = False,
    quiet: bool = False,
    scale_darks: bool = False,
    flat_state_path: Optional[Path] = None,
    picker_limit: int = 5,
) -> Statistics:
```

- **Before the `*`** — positional or keyword (required):
  `library_dir`, `blink_dir`, `date_dir_pattern`
- **After the `*`** — keyword-only (optional):
  `dry_run`, `quiet`, `scale_darks`, `flat_state_path`, `picker_limit`

Callers must name every optional argument:

```python
# CORRECT
stats = process_blink_directory(
    lib_path,
    blink_path,
    "YYYY-MM-DD",
    dry_run=True,
    scale_darks=True,
)

# WRONG — TypeError at runtime
stats = process_blink_directory(lib_path, blink_path, "YYYY-MM-DD", True, False, True)
```

### Guidelines

- Place `*` after the last required positional parameter
- All parameters with default values should appear after `*`
- Required parameters without defaults stay before `*`
- This applies to all project functions, not just public APIs

### Enforcement

- Python itself raises `TypeError` for violations — no linter needed
- Code reviewers should flag function definitions that have optional parameters without `*`
- Add `*` to existing functions opportunistically when making changes
