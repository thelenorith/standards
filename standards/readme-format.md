# README Format

Standard structure for ap-* project READMEs.

## Structure

1. Title
2. Badges
3. Brief description (1-2 sentences)
4. Documentation links (ap-base boilerplate)
5. Overview (what it does, key features)
6. Installation
7. Usage (with examples)

## Title

Use the package name as the title:

```markdown
# ap-<name>
```

Do not use prose titles like "Light Frame Organization Tool".

## Badges

Seven standard badges, formatted on two lines for readability:

**Line 1:** Workflow badges (Test, Coverage, Lint, Format, Type Check)
**Line 2:** Language and style badges (Python version, Black formatting)

```markdown
[![Test](https://github.com/jewzaam/ap-<name>/workflows/Test/badge.svg)](https://github.com/jewzaam/ap-<name>/actions/workflows/test.yml) [![Coverage](https://github.com/jewzaam/ap-<name>/workflows/Coverage%20Check/badge.svg)](https://github.com/jewzaam/ap-<name>/actions/workflows/coverage.yml) [![Lint](https://github.com/jewzaam/ap-<name>/workflows/Lint/badge.svg)](https://github.com/jewzaam/ap-<name>/actions/workflows/lint.yml) [![Format](https://github.com/jewzaam/ap-<name>/workflows/Format%20Check/badge.svg)](https://github.com/jewzaam/ap-<name>/actions/workflows/format.yml) [![Type Check](https://github.com/jewzaam/ap-<name>/workflows/Type%20Check/badge.svg)](https://github.com/jewzaam/ap-<name>/actions/workflows/typecheck.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/) [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
```

**Note:** The Type Check badge is optional for projects that don't have type checking configured. Projects without type checking should omit this badge, resulting in 6 badges total (4 workflow badges on line 1, 2 language/style badges on line 2).

## Description

One or two sentences immediately after badges. State what the tool does, not implementation details.

Good:
> A tool for organizing light frames based on FITS metadata.

Bad:
> This Python package uses astropy to read FITS headers and organize files into directories.

## Documentation Links

All projects must include standard boilerplate linking back to ap-base for comprehensive documentation:

```markdown
## Documentation

This tool is part of the astrophotography pipeline. For comprehensive documentation including workflow guides and integration with other tools, see:

- **[Pipeline Overview](https://github.com/jewzaam/ap-base/blob/devel/docs/index.md)** - Full pipeline documentation
- **[Workflow Guide](https://github.com/jewzaam/ap-base/blob/devel/docs/workflow.md)** - Detailed workflow with diagrams
- **[ap-<name> Guide](https://github.com/jewzaam/ap-base/blob/devel/docs/tools/ap-<name>.md)** - Detailed usage guide for this tool
```

Replace `<name>` with the actual project name (e.g., `ap-common`, `ap-cull-light`).

## Overview

Expand on the description. Cover:
- What problem it solves
- Key features (bulleted list)
- How it fits in the pipeline (if relevant)

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
pip install git+https://github.com/jewzaam/ap-<name>.git
\`\`\`
```

## Usage

Show the command-line interface with examples:

```markdown
## Usage

\`\`\`bash
python -m ap_<name>.<module> <source_dir> <dest_dir> [options]
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
