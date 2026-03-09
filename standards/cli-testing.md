# CLI Testing Standards

Unit testing conventions for CLI entry points (main() functions) in Python projects.

## Purpose

CLI tests verify that command-line arguments are correctly parsed and passed to
business logic functions. This prevents a common class of bugs where argument names
are mistyped when accessing the parsed args object.

## Dependencies

CLI tests require `pytest-mock>=3.0` for the `mocker` fixture used to patch `sys.argv` and mock business functions.

**Add to `pyproject.toml`:**
```toml
[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "pytest-cov>=4.0",
    "pytest-mock>=3.0",  # Required for CLI tests
    # ... other dev dependencies
]
```

## The Bug Class This Prevents

### Argument Name Mismatch Pattern

argparse converts `--scale-dark` to attribute `args.scale_dark` (hyphen becomes underscore).
Common bugs:

- Typo: `args.scale_darks` (plural) when only `args.scale_dark` exists -> AttributeError
- Case: `args.Scale_dark` when only `args.scale_dark` exists -> AttributeError
- Wrong delimiter: `args.scale.dark` when only `args.scale_dark` exists -> AttributeError

These bugs are invisible to:
- Linters (flake8, pylint) - cannot validate dynamic Namespace attributes
- Type checkers (mypy) - argparse.Namespace is untyped by default
- Unit tests - business logic tests mock the args object, never parse real CLI

**Only caught by:** Integration tests that exercise `main()` with real `sys.argv` patching.

## Required Coverage

Every module with a CLI entry point MUST have tests covering:

1. **Basic execution** - minimal required arguments
2. **Each boolean flag individually** - test both enabled and disabled states
3. **Each value argument** - verify type conversion and value passing
4. **Multiple flags combined** - ensure no interaction bugs
5. **Error conditions** - invalid args, missing required values
6. **Exit code validation** - verify EXIT_SUCCESS vs EXIT_ERROR

## Testing Pattern (Reference Implementation)

```python
from unittest.mock import patch

@patch("module.__main__.business_function")
@patch("module.__main__.validate_directories")
@patch("sys.argv", ["command", "arg1", "arg2", "--flag"])
def test_flag_name(mock_validate, mock_business):
    """Test that --flag is correctly mapped to parameter."""
    mock_validate.return_value = (True, None)
    mock_business.return_value = {"success": True}

    result = main()

    assert result == EXIT_SUCCESS
    # CRITICAL: Verify kwargs - catches args.attribute_name typos
    call_args = mock_business.call_args
    assert call_args.kwargs["param_name"] == expected_value
```

**Why this pattern works:**
- Patches `sys.argv` -> tests real argparse behavior
- Calls real `main()` -> exercises actual attribute access
- Mocks business function -> isolates argparse logic, fast tests
- Verifies `call_args.kwargs` -> catches attribute name mismatches immediately

If code has `args.scale_darks` but argparse defines `args.scale_dark`:
-> Test fails with `AttributeError` (production bug caught in test suite)

## Test File Organization

| Main() Location | Test File Name |
|----------------|----------------|
| `__main__.py` | `tests/test_main.py` |
| `cli.py` | `tests/test_cli.py` |
| Module file (e.g., `processor.py`) | `tests/test_<module>.py` |

Separate CLI tests from business logic tests for clarity.

## Examples by Flag Type

### Boolean Flag (BooleanOptionalAction)

Test all three states:

```python
def test_flag_enabled():
    """Test --flag sets value to True."""
    with patch("sys.argv", [..., "--flag"]):
        main()
        assert call_args.kwargs["param"] == True

def test_flag_disabled():
    """Test --no-flag sets value to False."""
    with patch("sys.argv", [..., "--no-flag"]):
        main()
        assert call_args.kwargs["param"] == False

def test_flag_default():
    """Test default value when flag omitted."""
    with patch("sys.argv", [...]):  # No flag
        main()
        assert call_args.kwargs["param"] == False  # or True, depending on default
```

### Value Argument

```python
def test_value_argument():
    """Test --path-pattern passes value correctly."""
    with patch("sys.argv", [..., "--path-pattern", "LIGHT.*"]):
        main()
        assert call_args.kwargs["path_pattern"] == "LIGHT.*"
```

### Multiple Flags

```python
def test_combined_flags():
    """Test --dryrun --quiet --scale-dark work together."""
    with patch("sys.argv", [..., "--dryrun", "--quiet", "--scale-dark"]):
        main()
        assert call_args.kwargs["dry_run"] == True
        assert call_args.kwargs["quiet"] == True
        assert call_args.kwargs["scale_darks"] == True
```

## Common Anti-Patterns

### DON'T: Test without verifying kwargs

```python
def test_flag():
    result = main()
    assert result == EXIT_SUCCESS  # Proves it didn't crash, but not that args worked
    mock_business.assert_called_once()  # Called, but with what args?
```

### DON'T: Only test that code runs

```python
def test_main():
    with patch("sys.argv", ["command"]):
        main()  # No assertions - worthless test
```

### DO: Verify exact kwargs/args

```python
def test_flag():
    result = main()
    assert result == EXIT_SUCCESS
    call_args = mock_business.call_args
    assert call_args.kwargs["scale_darks"] == True  # Catches typos
```

## Audit Checklist

When reviewing or adding CLI tests:

- [ ] Test file exists (`test_main.py`, `test_cli.py`, or equivalent)
- [ ] Imports main() and EXIT constants
- [ ] Uses `@patch("sys.argv", [...])` pattern for all tests
- [ ] Each CLI flag has at least one test
- [ ] Boolean flags test both enabled/disabled states
- [ ] Tests verify `call_args.kwargs` or `call_args.args`
- [ ] Multiple flags tested in combination
- [ ] Error conditions tested (invalid args, missing paths)
- [ ] Exit codes validated (EXIT_SUCCESS, EXIT_ERROR)
- [ ] Tests run and pass: `pytest tests/test_main.py -v`

**See:** [Testing Standards](testing.md) for general testing philosophy and patterns.
