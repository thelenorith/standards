# Naming Conventions

Standard naming patterns for Python projects.

## Repository Naming

Use lowercase, hyphenated names that clearly describe the project's purpose:

```
<project-name>
```

For project families with a shared prefix:

```
<prefix>-<descriptive-name>
```

## Package Naming

Python packages use underscores matching the repository name:

| Repository Name | Package Directory |
|----------------|-------------------|
| `my-project` | `my_project/` |
| `data-processor` | `data_processor/` |

## Naming Guidelines

1. **Be descriptive** - Names should convey what the project does
2. **Use lowercase** - All repository and package names are lowercase
3. **Hyphens in repos, underscores in packages** - `my-project` repo contains `my_project/` package
4. **Use singular nouns** - `record` not `records`, `header` not `headers`
5. **Keep names concise** - Avoid unnecessary words

## Module and File Naming

| Item | Convention | Example |
|------|-----------|---------|
| Module files | lowercase, underscored | `data_processor.py` |
| Test files | `test_<module>.py` | `test_data_processor.py` |
| Package directories | lowercase, underscored | `my_project/` |
| Constants | `UPPER_SNAKE_CASE` | `DEFAULT_TIMEOUT` |
| Functions | `lower_snake_case` | `process_data()` |
| Classes | `PascalCase` | `DataProcessor` |
