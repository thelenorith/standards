# Versioning Standards

Semantic versioning conventions for ap-* projects.

## Version Format

All projects use [Semantic Versioning](https://semver.org/):

```
X.Y.Z
```

| Component | Name | Incremented When |
|-----------|------|------------------|
| `X` | Major | Breaking changes |
| `Y` | Minor | New features (backward compatible) |
| `Z` | Patch | Bug fixes, tweaks, documentation |

## What Counts as a Breaking Change

A breaking change is anything that causes existing usage to fail or produce different results.

| Change | Breaking? | Rationale |
|--------|-----------|-----------|
| Rename a CLI argument | Yes | Existing scripts and automation break |
| Remove a CLI argument | Yes | Existing scripts and automation break |
| Change a CLI argument's default value | Yes | Existing behavior changes silently |
| Change CLI exit code meanings | Yes | Scripting logic breaks |
| Change output format (stdout) | Yes | Downstream consumers break |
| Add a new required CLI argument | Yes | Existing invocations fail |
| Add a new optional CLI argument | No | Existing invocations still work |
| Add a new feature behind a flag | No | No change to existing behavior |

## Integration Surface

The supported integration pattern for ap-* tools is the **command-line interface**.

| Integration Method | Status | Versioning Applies? |
|--------------------|--------|---------------------|
| CLI (command-line) | Supported | Yes - CLI is the public API |
| Python module import | Not supported | No - internal, may change without notice |
| REST/HTTP API | Not yet available | TODO |

**Do not import ap-* modules directly.** Internal function signatures, module layout, and return types may change in any release without a major version bump. The CLI is the contract.

<!-- TODO: Define an API layer for programmatic integration. Until then, CLI is the only stable interface. -->

## Version Increment Rules

### Major (`X`) - Breaking Changes

Increment major version when the CLI contract changes in an incompatible way.

**Examples:**

- `--blink-dir` renamed to `--blink-path`
- `--no-overwrite` removed
- Default behavior of `--scale-dark` changed from off to on
- Output format changed from tab-separated to JSON

### Minor (`Y`) - New Features

Increment minor version when new functionality is added without breaking existing usage.

**Examples:**

- New `--format` option added
- New subcommand added
- New output field appended (when consumers are tolerant of extra fields)
- Support for a new file type

### Patch (`Z`) - Bug Fixes and Tweaks

Increment patch version for fixes that correct behavior to match documented intent.

**Examples:**

- Fix crash on empty directory input
- Fix incorrect FITS header value extraction
- Fix `--quiet` flag not suppressing progress bars
- Documentation corrections
- Performance improvements with no behavior change

## Guidelines

1. **CLI is the public API** - Version the CLI contract, not internal code
2. **When in doubt, bump major** - A cautious major bump is better than a surprise break
3. **Reset lower components** - Bumping minor resets patch to 0; bumping major resets minor and patch to 0
4. **Tag releases** - Use git tags matching `vX.Y.Z` (e.g., `v1.2.0`)
5. **Start at 0.1.0** - New projects start at `0.1.0`; the `0.x` range signals pre-stable development where breaking changes may occur in minor releases
