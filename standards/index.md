# Project Standards

Standards for all ap-* astrophotography pipeline projects.

## Documents

| Standard | Description |
|----------|-------------|
| [Python Style](python-style.md) | Python coding style and best practices |
| [ap-common Usage](ap-common-usage.md) | Use shared constants from ap-common |
| [Naming](naming.md) | Project and package naming conventions |
| [Project Structure](project-structure.md) | Directory layout and required files |
| [README Format](readme-format.md) | README structure and content |
| [Makefile](makefile.md) | Build targets and conventions |
| [GitHub Workflows](github-workflows.md) | CI/CD pipeline configuration |
| [Testing](testing.md) | Unit testing conventions, TDD, and TEST_PLAN.md requirements |
| [CLI](cli.md) | Command-line interface conventions |
| [Logging & Progress](logging-progress.md) | Logging, progress indicators, and output |

## Templates

| Template | Description |
|----------|-------------|
| [TEST_PLAN.md](templates/TEST_PLAN.md) | Testing strategy documentation template |
| [Makefile](templates/Makefile) | Standard Makefile for ap-* projects |
| [workflows/](templates/workflows/) | GitHub Actions workflow templates |

## Guiding Principles

1. **Consistency** - All projects follow the same patterns
2. **Simplicity** - Minimal configuration, sensible defaults
3. **Automation** - CI catches issues before merge
4. **Discoverability** - Standard locations for everything

## Critical Constraints

**⚠️ Git LFS is prohibited**

- GitHub LFS has a $0 budget limit and is not funded
- Do not track binary files with Git LFS
- Generate test fixtures programmatically or use minimal files (< 100KB)
- Large binary files will cause CI failures and block development
