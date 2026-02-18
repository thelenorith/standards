# Integration Testing Standards

Cross-project integration testing for the ap-* tool suite.

This standard covers testing that validates multiple ap-* tools work together correctly. For per-project unit and integration tests, see [Testing Standards](testing.md).

## Purpose

Individual tools have their own test suites that validate internal behavior. Integration testing validates the **contracts between tools** — that the output of one tool is valid input for the next, and that a real workflow using multiple tools produces correct results.

Integration testing is what makes [lockstep versioning](versioning.md) and the [branching strategy](branching.md) work. If all tools share the same version, there must be a test suite that proves they actually work together at that version.

## Scope

| What is tested | Where it lives |
|----------------|---------------|
| Single function/method | Per-project `tests/` — see [Testing Standards](testing.md) |
| Multiple modules in one project | Per-project `tests/` — see [Testing Standards](testing.md) |
| Multiple ap-* tools in a workflow | Integration test suite (this standard) |

## What to Test

Integration tests exercise real CLI invocations across tools. They validate:

### Tool Chain Contracts

Test that the output of one tool is accepted as input by the next tool in a workflow.

**Example:** ap-cull-light produces a directory structure that ap-calibrate expects:

```python
def test_cull_output_feeds_calibrate(tmp_path):
    """Verify ap-cull-light output is valid input for ap-calibrate."""
    raw_dir = tmp_path / "raw"
    setup_test_lights(raw_dir)

    result = subprocess.run(
        ["ap-cull-light", "--input", str(raw_dir), "--output", str(tmp_path / "culled")],
        capture_output=True, text=True,
    )
    assert result.returncode == 0

    result = subprocess.run(
        ["ap-calibrate", "--input", str(tmp_path / "culled")],
        capture_output=True, text=True,
    )
    assert result.returncode == 0
```

### CLI Contract Stability

Test that CLI arguments documented in one tool's help text match what downstream tools or scripts expect. This catches breaking changes that per-project tests miss because they mock the CLI layer.

### End-to-End Workflows

Test complete user workflows from raw input to final output, exercising the real CLI of each tool in sequence. These are the most valuable integration tests because they mirror actual usage.

## Test Design

### Use Real CLI Invocations

Integration tests call tools via `subprocess.run`, not by importing Python modules. The CLI is the [public API](versioning.md) and the integration surface.

```python
# CORRECT - test the CLI contract
result = subprocess.run(["ap-cull-light", "--input", str(input_dir)], capture_output=True, text=True)

# WRONG - bypasses the CLI contract
from ap_cull_light.core import cull
cull(input_dir)
```

### Use Minimal Fixtures

Follow the same rules as [Testing Standards](testing.md): generate test data programmatically, keep fixtures small, no Git LFS.

```python
def setup_test_lights(directory):
    """Create minimal FITS files for integration testing."""
    directory.mkdir(parents=True, exist_ok=True)
    for i in range(3):
        create_minimal_fits(
            directory / f"light_{i}.fits",
            header_data={"IMAGETYP": "LIGHT", "EXPOSURE": 300},
        )
```

### Assert Outcomes, Not Internals

Integration tests verify external behavior — exit codes, output files, directory structures. They do not assert internal state, log messages, or implementation details.

```python
# GOOD - verifies the contract
assert result.returncode == 0
assert (output_dir / "master_dark.fits").exists()
assert get_fits_header(output_dir / "master_dark.fits", "IMAGETYP") == "DARK"

# BAD - testing internal implementation
assert "Processing 3 files" in result.stderr
```

## Test Organization

Integration tests live in a dedicated repository or directory, separate from individual project test suites:

```
ap-integration-tests/
├── pyproject.toml
├── Makefile
├── tests/
│   ├── conftest.py           # Shared fixtures, helper functions
│   ├── test_cull_calibrate.py
│   ├── test_end_to_end.py
│   └── fixtures/
│       └── README.md
└── TEST_PLAN.md
```

The integration test suite depends on all ap-* tools being installed. It does not vendor or bundle them.

## CI Strategy

Integration tests run on the same branches as individual project CI, aligned with the [branching strategy](branching.md):

| Trigger | What runs |
|---------|-----------|
| PR to `devel` (any ap-* project) | Per-project CI (unit tests, lint, etc.) |
| Push to `devel` (after merge) | Integration test suite against `devel` HEAD of all tools |
| PR to `stable-X.Y` | Per-project CI + integration test suite against `stable-X.Y` HEAD of all tools |
| Tag `vX.Y.Z` | Full integration test suite as release gate |

### Installation for CI

The integration test CI installs all ap-* tools from their respective branches before running tests:

```yaml
- name: Install all ap-* tools from devel
  run: |
    pip install git+https://github.com/jewzaam/ap-common.git@devel
    pip install git+https://github.com/jewzaam/ap-cull-light.git@devel
    # ... additional tools
```

This ensures tests run against the actual code on the branch, not a published release.

### Failure Handling

An integration test failure blocks the release. If integration tests fail on `devel`, the failing change must be fixed before cutting a `stable-X.Y` branch. If integration tests fail on `stable-X.Y`, the release tag is not created until the fix lands.

## When to Add Integration Tests

| Event | Action |
|-------|--------|
| New tool added to the suite | Add tests for its interaction with existing tools |
| Tool output format changes | Add or update contract tests for downstream consumers |
| User reports cross-tool bug | Add regression test (TDD per [Testing Standards](testing.md)) |
| New workflow documented | Add end-to-end test covering the workflow |

## Relationship to Per-Project Tests

Integration testing complements, not replaces, per-project testing:

| Concern | Per-project tests | Integration tests |
|---------|-------------------|-------------------|
| Internal logic | Yes | No |
| Mocking | Extensive | Minimal (real tools) |
| Speed | Fast (seconds) | Slower (real I/O) |
| Failure specificity | Exact function | Somewhere in the chain |
| Runs on | Every PR | After merge + release gates |
| Validates | Correctness of one tool | Compatibility across tools |
