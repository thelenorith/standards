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
status = check_calibration_status(image_dir, source_dir, debug, allow_bias)

# CORRECT: Named optional parameters
status = check_calibration_status(
    image_dir,
    source_dir,
    debug=debug,
    allow_bias=allow_bias
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
