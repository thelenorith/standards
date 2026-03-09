# README Format

Standard structure for project READMEs.

## Structure

1. Title
2. Badges
3. Brief description (1-2 sentences)
4. Documentation links
5. Overview (what it does, key features)
6. Installation
7. Usage (with examples)

## Title

Use the package name as the title:

```markdown
# <project-name>
```

Do not use prose titles like "Light Frame Organization Tool".

## Badges

Standard badges, formatted on two lines for readability:

**Line 1:** Workflow badges (Test, Coverage, Lint, Format, Type Check)
**Line 2:** Language and style badges (Python version, Black formatting)

```markdown
[![Test](https://github.com/<owner>/<project-name>/workflows/Test/badge.svg)](https://github.com/<owner>/<project-name>/actions/workflows/test.yml) [![Coverage](https://github.com/<owner>/<project-name>/workflows/Coverage%20Check/badge.svg)](https://github.com/<owner>/<project-name>/actions/workflows/coverage.yml) [![Lint](https://github.com/<owner>/<project-name>/workflows/Lint/badge.svg)](https://github.com/<owner>/<project-name>/actions/workflows/lint.yml) [![Format](https://github.com/<owner>/<project-name>/workflows/Format%20Check/badge.svg)](https://github.com/<owner>/<project-name>/actions/workflows/format.yml) [![Type Check](https://github.com/<owner>/<project-name>/workflows/Type%20Check/badge.svg)](https://github.com/<owner>/<project-name>/actions/workflows/typecheck.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/) [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
```

**Note:** The Type Check badge is optional for projects that don't have type checking configured. Projects without type checking should omit this badge, resulting in 6 badges total (4 workflow badges on line 1, 2 language/style badges on line 2).

## Description

One or two sentences immediately after badges. State what the tool does, not implementation details.

Good:
> A tool for organizing data files based on metadata.

Bad:
> This Python package uses the standard library to read file headers and organize files into directories.

## Documentation Links

Projects that are part of a larger suite should include links to the parent documentation:

```markdown
## Documentation

This tool is part of the <suite name>. For comprehensive documentation:

- **[Overview](<link>)** - Full documentation
- **[<project-name> Guide](<link>)** - Detailed usage guide for this tool
```

## Overview

Expand on the description. Cover:
- What problem it solves
- Key features (bulleted list)
- How it fits in the project suite (if relevant)

Keep it brief. Users want to know what it does, not how.

## Installation

Two methods:

```markdown
## Installation

### Development

\`\`\`bash
make install-dev
\`\`\`

### From Git

\`\`\`bash
pip install git+https://github.com/<owner>/<project-name>.git
\`\`\`
```

## Usage

Show the command-line interface with examples:

```markdown
## Usage

\`\`\`bash
python -m <package_name>.<module> <source_dir> <dest_dir> [options]
\`\`\`

### Options

| Option | Description |
|--------|-------------|
| `--debug` | Enable debug output |
| `--dryrun` | Preview without changes |
| `--quiet` / `-q` | Suppress non-essential output |
```

Include 1-2 concrete examples with real-looking paths.

## What to Avoid

- Implementation details (test file names, internal functions)
- Verbose explanations of obvious things
- Changelog or version history
- Contributor guidelines (use CONTRIBUTING.md if needed)
- Duplicate information from other sections
- License section (LICENSE file exists)
