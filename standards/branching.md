# Branching Strategy

Branch model for ap-* projects using `devel` and `stable-X.Y` branches.

## Branch Model

There is no `main` branch. Two types of long-lived branches exist:

| Branch | Purpose | Accepts |
|--------|---------|---------|
| `devel` | Integration branch for all development | Feature PRs, dependency updates, refactors |
| `stable-X.Y` | Released version, receives fixes only | Bug fix PRs, security patches |

### devel

The `devel` branch is the primary branch. All feature work lands here via pull requests. It always represents the latest development state and is the base for cutting new releases.

- All PRs target `devel` unless they are hotfixes for a released stable branch
- CI runs on every push and PR to `devel`
- The branch is never deleted

### stable-X.Y

A `stable-X.Y` branch is created when `devel` is ready for release. It represents a released version that only receives patch-level fixes going forward.

- Created from `devel` at release time
- Only bug fixes and security patches are merged here
- Each merge bumps the patch version (X.Y.Z where Z increments)
- Tagged with `vX.Y.0` at creation, `vX.Y.1`, `vX.Y.2`, etc. for patches

## No Feature Branches

There are no long-lived feature branches in the repository. Development happens in short-lived branches that exist only as part of a pull request:

```
developer fork/clone
  └── short-lived branch (PR) ──► devel
```

The PR branch is the feature branch. It is created, reviewed, merged, and deleted. If a feature takes multiple PRs, each PR should be independently mergeable and leave `devel` in a working state.

## Release Workflow

### Cutting a New Release

When `devel` has accumulated enough features for a release:

```
1. Create stable-X.Y from devel
2. Update version to X.Y.0 in all projects
3. Tag vX.Y.0
4. Bump devel to the next development version
```

**Example:** releasing 1.3

```bash
git checkout devel
git checkout -b stable-1.3
# Update versions to 1.3.0 across all projects
git tag v1.3.0
git push origin stable-1.3 v1.3.0

# Back on devel, bump to next development version
git checkout devel
# Update versions to 1.4.0.dev0 or similar marker
```

### Hotfix Workflow

When a bug is found in a released `stable-X.Y`:

```
1. Create a PR targeting stable-X.Y
2. Fix the bug (with regression test per testing standards)
3. Merge to stable-X.Y
4. Tag vX.Y.Z (incremented patch)
5. Cherry-pick the fix forward to devel (and any newer stable branches)
```

Cherry-picking forward is critical. Fixes must not be lost when the next stable branch is cut from `devel`.

**Example:** fixing a bug in stable-1.3

```bash
# Fix lands on stable-1.3 via PR
git checkout stable-1.3
git tag v1.3.1
git push origin stable-1.3 v1.3.1

# Cherry-pick to devel
git checkout devel
git cherry-pick <fix-commit>
git push origin devel
```

### Why Cherry-Pick (Not Merge)

Cherry-picking gives exact control over which commits move between branches. Merging a stable branch into `devel` would pull in release-specific changes (version bumps, changelog entries) that do not belong in `devel`. Cherry-pick the fix, not the release metadata.

## Lockstep Versioning

All ap-* tools share the same `X.Y` version on every release. When `stable-X.Y` is cut, all tools are released at `X.Y.0` regardless of whether each tool changed individually.

### Rationale

- **Simple compatibility** — users install all tools at the same version and they work together
- **No compatibility matrix** — no need to track which version of ap-cull-light works with which version of ap-common
- **Simple integration testing** — test all tools at HEAD of the same branch
- **Simple packaging** — one version number for the entire suite

### Trade-Off

Some tools will get version bumps with no functional changes. This is intentional overhead in exchange for dramatically simpler compatibility, testing, and user experience. A version bump with no changes is a small cost; debugging a version mismatch across tools is a large one.

### Version Increment at Release Time

The `X.Y` version is determined by the nature of changes accumulated in `devel` since the last release, following [Versioning Standards](versioning.md):

| Changes in devel | Version bump |
|-------------------|-------------|
| Any breaking CLI change in any tool | Major (X) |
| New features, no breaking changes | Minor (Y) |

Patch versions (Z) are only used on stable branches for hotfixes.

## Supported Stable Branches

Not every `stable-X.Y` branch needs active maintenance. Define a support policy:

| Policy | Description |
|--------|-------------|
| Current | The latest `stable-X.Y` — receives bug fixes and security patches |
| Previous | The prior `stable-X.Y` — receives critical bug fixes and security patches only |
| End of life | Older branches — no patches, users should upgrade |

This limits the maintenance burden while giving users a migration window. Adjust the window as the project matures.

## Branch Protection

| Branch | Rules |
|--------|-------|
| `devel` | Require PR, require CI pass, no direct push |
| `stable-*` | Require PR, require CI pass, no direct push |

Direct pushes to `devel` or any `stable-X.Y` branch are prohibited. All changes go through pull requests with passing CI.

## Default Branch

Set `devel` as the default branch in GitHub. This ensures:

- New clones check out `devel`
- PRs default to targeting `devel`
- GitHub UI shows `devel` as the landing page

## Summary

```
                    ┌─── PR (bug fix) ──► stable-1.2 ── tag v1.2.1
                    │                         │
                    │                    cherry-pick
                    │                         │
                    │                         ▼
 ── devel ◄── PR ◄── PR ◄── PR ◄── PR ◄── PR ──
       │
       └──► stable-1.3 ── tag v1.3.0
```

- `devel` is the trunk where all feature work integrates
- `stable-X.Y` branches are cut for releases
- Hotfixes target the affected stable branch and are cherry-picked forward
- All tools share the same `X.Y` version
- No `main` branch exists
