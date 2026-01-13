# report

[Agent Skill](https://agentskills.io) for creating investigation and analysis reports.

## Overview

Compiles investigation and debugging results into structured reports in GitHub Flavored Markdown format.

## Usage

```
/report
```

## Features

- Standardized report structure
- Auto-generated timestamped filenames
- GitHub Flavored Markdown format

## Filename Format

```
{topic}-{YYYY-MM-DD}-{HHmm}.md
```

Example: `api-error-investigation-2025-01-13-1430.md`

## Save Location

Priority order:
1. `docs/reports/`
2. `docs/`
3. Project root

## Report Structure

- **Summary**: Purpose and content summary
- **Background**: Investigation background
- **Investigation/Analysis Details**: Detailed content
- **Findings**: Discoveries
- **Recommendations**: Recommended actions
- **Conclusion**: Summary
- **Additional Information**: Referenced files, etc.

## Details

See [SKILL.md](SKILL.md) for detailed templates.
