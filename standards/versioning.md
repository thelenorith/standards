# Versioning Standards

Semantic versioning conventions for ap-* projects. See [Branching Strategy](branching.md) for how versions map to branches.

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
| Change output format (stdout/stderr) | No | Output is not a stable contract |
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

## Lockstep Versioning

All ap-* tools share the same `X.Y` version on every release. When a `stable-X.Y` branch is cut from `devel`, all tools are released at version `X.Y.0` together.

| Aspect | Rule |
|--------|------|
| Major/minor version | Same across all ap-* tools at release time |
| Patch version | Independent per tool (hotfixes may not apply to all tools) |
| Version source of truth | Git tags on the `stable-X.Y` branch |

### Why Lockstep

- **No compatibility matrix** — users install all tools at the same X.Y and they work together
- **Simple integration testing** — test all tools at HEAD of the same branch
- **Simple packaging** — one version number for the entire suite
- **Clear user communication** — "upgrade to 1.3" means upgrade everything to 1.3

Tools that have no changes in a release still receive the version bump. This is intentional overhead in exchange for simpler compatibility, testing, and user experience.

## Version-Branch Relationship

Versions are tied to the [branching model](branching.md):

| Branch | Version state |
|--------|--------------|
| `devel` | Next unreleased version (development) |
| `stable-X.Y` | Released `X.Y.Z` (patch increments for hotfixes) |

- The `X.Y` in `stable-X.Y` is determined at release time based on what changed in `devel` since the last release
- Patch versions only appear on stable branches via hotfixes
- Tags (`vX.Y.Z`) are only created on stable branches, never on `devel`

## Guidelines

1. **CLI is the public API** — version the CLI contract, not internal code
2. **When in doubt, bump major** — a cautious major bump is better than a surprise break
3. **Reset lower components** — bumping minor resets patch to 0; bumping major resets minor and patch to 0
4. **Tag releases** — use git tags matching `vX.Y.Z` (e.g., `v1.2.0`) on `stable-X.Y` branches
5. **Start at 0.1.0** — new projects start at `0.1.0`; the `0.x` range signals pre-stable development where breaking changes may occur in minor releases
6. **Lockstep release** — all ap-* tools share the same `X.Y` at release time; see [Branching Strategy](branching.md) for the release workflow
