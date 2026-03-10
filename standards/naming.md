# Naming Conventions

Standard naming patterns for Python projects.

## Project Group Naming

Projects that belong to a related suite use a shared prefix to indicate membership:

```
<prefix>-<verb>-<qualifier?>-<noun>-to-<destination?>
```

| Component | Required | Description |
|-----------|----------|-------------|
| `prefix` | Yes | Project group identifier (e.g., `dp` for data-pipeline) |
| `verb` | Yes | Action the tool performs |
| `qualifier` | No | Modifier for the noun (e.g., `raw`) |
| `noun` | Yes | What the tool operates on (always singular) |
| `destination` | No | Where data moves to |

### Defining a Verb Taxonomy

Each project group should define a consistent verb taxonomy. Example for a data pipeline:

| Verb | Action |
|------|--------|
| `copy` | Duplicate to a destination (source retained) |
| `create` | Generate new artifacts from inputs |
| `cull` | Filter/reject based on quality metrics |
| `preserve` | Save metadata to a persistent store |
| `move` | Transfer from one location to another |
| `delete` | Remove files or records |
| `empty` | Clean up (e.g., remove empty directories) |

### Defining a Noun Taxonomy

Each project group should define consistent nouns for the domain:

| Noun | Definition |
|------|------------|
| `record` | A single data record or file |
| `batch` | A processed/aggregated artifact |
| `header` | Metadata associated with a record |

### Example Project Names

| Project | Pattern | Purpose |
|---------|---------|---------|
| `dp-move-raw-record-to-staging` | prefix-verb-qualifier-noun-to-dest | Move raw records to staging |
| `dp-cull-record` | prefix-verb-noun | Filter poor quality records |
| `dp-preserve-header` | prefix-verb-noun | Save metadata to persistent store |
| `dp-create-batch` | prefix-verb-noun | Create batch from raw inputs |
| `dp-move-batch-to-archive` | prefix-verb-noun-to-dest | Move batches to archive |
| `dp-copy-batch-to-staging` | prefix-verb-noun-to-dest | Copy batches to staging |
| `dp-common` | prefix-common | Shared utilities (exception to verb pattern) |

## Package Naming

Python packages use underscores matching the repository name:

| Repository Name | Package Directory |
|----------------|-------------------|
| `dp-cull-record` | `dp_cull_record/` |
| `dp-common` | `dp_common/` |

## Naming Guidelines

1. **Start with a verb** - Every tool name begins with an action (after the group prefix)
2. **Use singular nouns** - `record` not `records`, `header` not `headers`
3. **Include destination when moving** - Use `-to-{dest}` suffix for tools that relocate data
4. **Use qualifiers sparingly** - Only when distinguishing between variants (e.g., `raw` vs processed)
5. **Use lowercase** - All repository and package names are lowercase
6. **Hyphens in repos, underscores in packages** - `dp-cull-record` repo contains `dp_cull_record/` package

## Module and File Naming

| Item | Convention | Example |
|------|-----------|---------|
| Module files | lowercase, underscored | `data_processor.py` |
| Test files | `test_<module>.py` | `test_data_processor.py` |
| Package directories | lowercase, underscored | `dp_cull_record/` |
| Constants | `UPPER_SNAKE_CASE` | `DEFAULT_TIMEOUT` |
| Functions | `lower_snake_case` | `process_data()` |
| Classes | `PascalCase` | `DataProcessor` |
