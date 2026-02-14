# Testing Standards

Unit testing conventions for ap-* projects.

## Testing Philosophy

Tests exist to prevent regressions and validate functionality. A test that cannot catch a real bug provides false confidence and wastes maintenance effort.

**Guiding principles:**

1. **Tests must have teeth** - Every test should be capable of failing when the code it tests is broken
2. **TDD for bug fixes** - Write a failing test before fixing a bug to prove the test catches the defect
3. **Functionality over coverage** - 80% meaningful coverage beats 100% superficial coverage
4. **Document the "why"** - Each project maintains a TEST_PLAN.md explaining testing rationale

## Unit vs Integration Tests

Understanding the distinction ensures tests are placed correctly and provide appropriate feedback.

### Unit Tests

Test a single function or method in complete isolation.

| Characteristic | Requirement |
|----------------|-------------|
| Scope | Single function/method |
| Dependencies | All mocked (no real I/O) |
| Filesystem | `tmp_path` only, programmatically generated |
| Failure meaning | Exact location of bug is known |

**Example - Pure unit test:**

```python
def test_normalize_date_iso_format(self):
    """Test date normalization with ISO format input."""
    result = normalize_date("2024-01-15")
    assert result == "2024-01-15"
```

**Example - Unit test with mocking:**

```python
@patch("ap_common.move_file")
def test_reject_image_moves_file(self, mock_move_file, tmp_path):
    """Test that reject_image calls move_file with correct arguments."""
    source = tmp_path / "source" / "test.fits"
    source.parent.mkdir(parents=True)
    source.write_text("test")

    reject_image(str(source), reject_dir="/reject", source_dir=str(tmp_path))

    mock_move_file.assert_called_once()
    assert "reject" in str(mock_move_file.call_args)
```

### Integration Tests

Test multiple components working together, verifying contracts between modules.

| Characteristic | Requirement |
|----------------|-------------|
| Scope | Multiple functions/modules |
| Dependencies | Minimal mocking, real interactions |
| Filesystem | May use real fixtures (small files) |
| Failure meaning | Something is broken, investigation needed |

**Example - Integration test:**

```python
def test_workflow_darks_only(self, tmp_path):
    """Test full workflow with only dark frames."""
    # Create actual test files
    dark_dir = tmp_path / "darks"
    dark_dir.mkdir()
    create_minimal_fits(dark_dir / "dark1.fits", {"IMAGETYP": "DARK"})

    # Run actual workflow (not mocked)
    result = process_calibration_directory(str(tmp_path))

    assert result.dark_count == 1
    assert result.bias_count == 0
```

### Where to Draw the Line

| Scenario | Test Type | Rationale |
|----------|-----------|-----------|
| String parsing/formatting | Unit | Pure logic, no dependencies |
| File path construction | Unit | Logic only, mock filesystem checks |
| FITS header extraction | Unit | Mock `astropy.io.fits` |
| CLI argument parsing | Unit | Mock `sys.argv` |
| Full file processing workflow | Integration | Tests real component interaction |
| Directory traversal + filtering | Integration | Multiple modules cooperating |

## Test-Driven Development (TDD)

TDD is **required** for bug fixes to existing functionality. New features follow standard test-after development.

### TDD Workflow for Bug Fixes

```
1. Reproduce    - Confirm the bug exists
2. Write test   - Create a test that exposes the bug
3. Verify red   - Run test, confirm it FAILS
4. Implement    - Write the minimal fix
5. Verify green - Run test, confirm it PASSES
6. Commit       - Commit test and fix together
```

### Bug Fix Test Documentation

Link tests to the bug they validate:

```python
def test_filename_override_takes_precedence(self):
    """
    Regression test for https://github.com/jewzaam/ap-common/issues/15

    Bug: Master dark with EXPOSURE in filename used FITS header value
    instead of filename value.

    Fix: Filename-parsed values now take precedence over FITS headers
    when file_naming_override=True.
    """
    # ... test implementation
```

## CI Validation for Bug Fixes

Bug fix commits **must** include regression tests. CI enforces this for commits matching bug fix patterns.

### Commit Message Patterns

CI identifies bug fixes by these patterns in commit messages:

- `fix:` or `fix(scope):` (conventional commits)
- `Fixes #123` or `Closes #123` (GitHub issue references)
- `Bug:` prefix

### CI Validation Behavior

When a commit matches a bug fix pattern, CI performs additional validation:

1. Identifies test files added or modified in the commit
2. Checks out the commit's parent (pre-fix state)
3. Applies only the test changes (not the fix)
4. Runs the new/modified tests
5. **Expects tests to FAIL** - if they pass, the test doesn't catch the bug

### Bypassing Validation

For commits that match bug fix patterns but don't require regression tests (e.g., documentation fixes, typo corrections), add `[skip-regression-check]` to the commit message.

### What This Does NOT Apply To

- New feature development
- Refactoring (behavior unchanged)
- Performance improvements
- Documentation changes
- Dependency updates

## Manual Review Protocol

When reviewing bug fix PRs, verify the regression test:

### Review Checklist

1. **Test exists** - Is there a new or modified test for the bug?
2. **Test is specific** - Does it target the exact bug, not general behavior?
3. **Test documents the bug** - Does the docstring explain what was broken?
4. **Test would fail without fix** - Mentally (or actually) revert the fix - would the test catch it?

### Verification Steps (Optional but Recommended)

```bash
git checkout <pr-branch>
git log --oneline -5              # Identify the fix commit
git revert --no-commit <fix-commit>  # Temporarily undo fix
pytest tests/test_module.py -k "test_for_bug"  # Should FAIL
git checkout .                    # Restore fix
```

## TEST_PLAN.md

Each project **must** have a `TEST_PLAN.md` in the repository root documenting testing rationale.

See [TEST_PLAN.md Template](templates/TEST_PLAN.md) for the required structure.

The TEST_PLAN.md serves as:

- Single source of truth for testing decisions
- Onboarding documentation for contributors
- Audit trail for test coverage rationale

## Framework

Use pytest with pytest-cov for coverage.

## Directory Structure

```
tests/
├── __init__.py
├── conftest.py        # Shared fixtures
├── test_<module>.py   # Unit tests (one per module)
├── test_<module>_integration.py  # Integration tests (optional)
└── fixtures/          # Test data files
    └── README.md
```

## Test Isolation

Tests must be completely isolated:

| Rule | Rationale |
|------|-----------|
| No real filesystem access | Tests must not read/write outside `tmp_path` |
| No mutation of source files | Never modify files in the repo |
| No persistent state | Each test starts clean |
| All created files are cleaned up | Use `tmp_path` fixture for automatic cleanup |

Use pytest's `tmp_path` fixture for any file operations:

```python
def test_copy_file(tmp_path):
    source = tmp_path / "source.fits"
    source.write_bytes(b"test")
    dest = tmp_path / "dest.fits"

    copy_file(str(source), str(dest))

    assert dest.exists()
```

## Test Data (Fixtures)

**DO NOT USE GIT LFS**

Git LFS has a $0 budget limit and is not funded for these projects. Large binary files will cause CI failures and block development.

Store test data files in `tests/fixtures/`. Prefer small, minimal test files:

- **Generate programmatically** when possible (mock FITS headers, minimal valid files)
- **Keep fixtures small** - only what's needed to test functionality
- **Avoid large binary files** - they bloat the repository
- **Document fixtures** - add `tests/fixtures/README.md` explaining each file's purpose

Example of generating minimal test data:

```python
from astropy.io import fits
import numpy as np

def create_minimal_fits(path, header_data=None):
    """Create minimal valid FITS file for testing."""
    data = np.zeros((10, 10), dtype=np.uint16)
    hdu = fits.PrimaryHDU(data)
    if header_data:
        for key, value in header_data.items():
            hdu.header[key] = value
    hdu.writeto(path, overwrite=True)
```

## Naming

| Item | Pattern | Example |
|------|---------|---------|
| Test files | `test_<module>.py` | `test_move.py` |
| Test functions | `test_<function>_<scenario>` | `test_build_path_missing_camera_raises` |
| Test classes | `Test<Class>` | `TestMetadataExtraction` |
| Bug fix tests | `test_<function>_<issue>` | `test_exposure_override_issue_15` |

## Test Organization

One test file per module:

```
ap_<name>/
├── move.py
└── config.py

tests/
├── test_move.py
└── test_config.py
```

For modules with significant integration testing needs:

```
tests/
├── test_move.py              # Unit tests
├── test_move_integration.py  # Integration tests
└── test_config.py
```

## Coverage

Target 80%+ line coverage of meaningful code paths.

```bash
make coverage
```

Coverage metrics are a floor, not a ceiling. High coverage with weak assertions provides false confidence.

## What to Test

- Public functions and methods
- Edge cases (empty input, missing keys, boundary values)
- Error conditions (raises appropriate exceptions)
- Bug fixes (regression tests with issue links)

## What Not to Test

- Private functions (test through public interface)
- Third-party library behavior
- Configuration constants
- Logging output (unless logging IS the functionality)

## Common Anti-Patterns

Avoid these testing mistakes:

### Testing That Code Runs (Not That It Works)

```python
# BAD - only tests that no exception is raised
def test_process_file(tmp_path):
    process_file(str(tmp_path / "test.fits"))
    # No assertions!

# GOOD - verifies expected behavior
def test_process_file_creates_output(tmp_path):
    input_file = tmp_path / "test.fits"
    create_minimal_fits(input_file)

    process_file(str(input_file))

    output_file = tmp_path / "test_processed.fits"
    assert output_file.exists()
    assert get_header(output_file, "PROCESSED") == "TRUE"
```

### Accepting Errors as Success

```python
# BAD - treats failure as success
def test_move_file(tmp_path):
    try:
        move_file(source, dest)
        assert dest.exists()
    except PermissionError:
        assert dest.exists()  # Why would this be acceptable?

# GOOD - clear expectations
def test_move_file(tmp_path):
    source = tmp_path / "source.fits"
    source.write_bytes(b"test")
    dest = tmp_path / "dest.fits"

    move_file(str(source), str(dest))

    assert dest.exists()
    assert not source.exists()
```

### Testing Logging Instead of Behavior

```python
# BAD - only verifies logging, not file handling
def test_invalid_value_handling(mock_logger):
    process_file({"value": "invalid"})
    mock_logger.warning.assert_called()
    # But what happened to the file? Was it skipped? Rejected? Processed anyway?

# GOOD - verifies actual behavior
def test_invalid_value_skips_file(tmp_path):
    result = process_file({"value": "invalid", "filename": "test.fits"})

    assert result.skipped_count == 1
    assert "test.fits" in result.skipped_files
```
