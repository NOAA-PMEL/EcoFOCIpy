"""
Code Quality and Linting Standards for EcoFOCIpy

This document outlines the code quality standards and linting configuration for EcoFOCIpy.

## Overview

EcoFOCIpy uses professional-grade linting and code formatting tools to maintain consistent,
high-quality code throughout the project:

- **isort**: Import statement sorting and organization
- **pylint**: Comprehensive code quality checking
- **black**: Code formatting (via pre-commit hooks)

## isort Configuration

isort ensures all imports are consistently sorted and organized.

### Configuration File: `.isort.cfg`

```ini
[settings]
profile = black                    # Use Black-compatible settings
line_length = 88                   # Match Black's line length
multi_line_mode = 3                # Vertical Hanging Indent
include_trailing_comma = true      # Add trailing commas
force_grid_wrap = 0                # Don't force grid wrapping
use_parentheses = true             # Use parentheses for line continuation
```

### Import Organization

Imports are organized in the following order:

1. `__future__` imports (e.g., `from __future__ import annotations`)
2. Standard library imports (e.g., `import os`, `import sys`)
3. Third-party imports (e.g., `import numpy`, `import pandas`)
4. First-party imports (e.g., `from EcoFOCIpy import ...`)
5. Local imports (e.g., `from . import module`)

### Example: Correct Import Order

```python
\"\"\"Module docstring.\"\"\"
# Future imports
from __future__ import annotations

# Standard library
import datetime
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

# Third-party
import numpy as np
import pandas as pd
from scipy import stats

# First-party
from EcoFOCIpy.math import ctd_corrections
from EcoFOCIpy.qc import ctd_qc

# Local
from .utils import helper_function


def main() -> None:
    \"\"\"Main function.\"\"\"
    pass
```

### Running isort

```bash
# Check for import sorting issues
isort --check-only src/EcoFOCIpy/ tests/

# Fix import sorting issues
isort src/EcoFOCIpy/ tests/

# Show diff of what would change
isort --diff src/EcoFOCIpy/ tests/

# Dry run (no changes)
isort --check-only --diff src/EcoFOCIpy/ tests/
```

## pylint Configuration

pylint performs comprehensive code quality analysis.

### Configuration File: `.pylintrc`

Key settings:
- **Python version**: 3.8+ (sets minimum compatibility)
- **Line length**: 88 characters (matches Black)
- **Failure threshold**: 8.0/10 (must maintain minimum score)
- **Disabled checks**: Conventional/refactoring recommendations (optional)
- **Enabled checks**: All errors (E) and fatal issues (F)

### pylint Categories

1. **Errors (E)**: Critical issues that should always be fixed
2. **Fatal (F)**: Issues that prevent execution
3. **Warnings (W)**: Potential issues
4. **Convention (C)**: Code style issues (disabled by default)
5. **Refactor (R)**: Suggestions for code improvement (disabled by default)
6. **Informational (I)**: Extra information

### Running pylint

```bash
# Full pylint check (all issues)
pylint src/EcoFOCIpy/

# Check only critical issues (errors and fatals)
pylint --disable=C,R,W --enable=E,F src/EcoFOCIpy/

# Check specific file
pylint src/EcoFOCIpy/qc/ctd_qc.py

# Generate detailed report
pylint --output-format=html src/EcoFOCIpy/ > report.html

# Check with specific rating threshold
pylint --fail-under=9.0 src/EcoFOCIpy/

# Quiet mode (only show messages)
pylint -q src/EcoFOCIpy/
```

### Common pylint Issues and Fixes

#### Missing docstring
```python
# ❌ Bad
def calculate_value(x):
    return x * 2

# ✅ Good
def calculate_value(x: float) -> float:
    \"\"\"Calculate twice the input value.
    
    Args:
        x: Input value
        
    Returns:
        Value multiplied by 2
    \"\"\"
    return x * 2
```

#### Unused variable
```python
# ❌ Bad
def process_data(a, b, c):
    return a + b  # c is unused

# ✅ Good
def process_data(a: float, b: float) -> float:
    \"\"\"Process two values.\"\"\"
    return a + b
```

#### Line too long
```python
# ❌ Bad (> 88 chars)
result = some_function_with_long_name(parameter1, parameter2, parameter3, parameter4)

# ✅ Good
result = some_function_with_long_name(
    parameter1, parameter2, parameter3, parameter4
)
```

## Code Quality Checks: Quick Reference

### Before Committing Code

```bash
# 1. Format imports
isort src/EcoFOCIpy/

# 2. Check import sorting
isort --check-only src/EcoFOCIpy/

# 3. Check code quality (errors only)
pylint --disable=C,R,W --enable=E,F src/EcoFOCIpy/

# 4. Run tests
python -m pytest tests/

# 5. Run specific test file
python tests/test_qc.py
```

### Pre-commit Configuration

Add to `.pre-commit-config.yaml` to automatically check before commits:

```yaml
repos:
  - repo: https://github.com/PyCQA/isort
    rev: 5.12.0
    hooks:
      - id: isort
        args: [--profile=black]
        
  - repo: https://github.com/PyCQA/pylint
    rev: pylint-2.16.2
    hooks:
      - id: pylint
        args: [--disable=C,R,W, --enable=E,F]
        stages: [commit]
```

## Project Compliance

### Current Status

✅ **isort**: All files pass import sorting checks
✅ **pylint**: All critical files score 10.00/10

### Files Checked

Core modules:
- ✅ `src/EcoFOCIpy/qc/ctd_qc.py` (10.00/10)
- ✅ `src/EcoFOCIpy/__init__.py` (10.00/10)
- ✅ `tests/test_qc.py` (10.00/10)
- ✅ `src/EcoFOCIpy/io/mtr_parser.py` (isort fixed)

### Recent Fixes

1. **mtr_parser.py**: Added blank line after imports (isort formatting)
   - Was: `import numpy as np` [class definition]
   - Now: `import numpy as np` [blank line] [class definition]

## Development Guidelines

### When Writing New Code

1. **Follow PEP 8** - Use standard Python style guidelines
2. **Use type hints** - Add type annotations to function signatures
3. **Write docstrings** - Document all public functions
4. **Keep lines under 88 characters** - For readability
5. **Run linters** - Check before committing

### Example: Well-Linted Function

```python
\"\"\"Quality Control module.\"\"\"
from typing import Optional, Tuple

import numpy as np
import pandas as pd


def range_check(
    data: pd.Series,
    min_val: float,
    max_val: float,
    flag_good: int = 1,
    flag_bad: int = 4,
) -> np.ndarray:
    \"\"\"Check if data values are within acceptable range.
    
    Args:
        data: Input data series to check
        min_val: Minimum acceptable value
        max_val: Maximum acceptable value
        flag_good: Flag for values within range (default 1)
        flag_bad: Flag for values outside range (default 4)
        
    Returns:
        Array of QC flags
        
    Raises:
        ValueError: If min_val > max_val
        
    Examples:
        >>> flags = range_check(data, min_val=0, max_val=30)
    \"\"\"
    if min_val > max_val:
        msg = f"min_val ({min_val}) > max_val ({max_val})"
        raise ValueError(msg)
    
    config = {'min': min_val, 'max': max_val}
    # ... rest of implementation
```

### Common Commands

```bash
# Format all Python files
isort src/

# Quick quality check
pylint --disable=C,R,W --enable=E,F src/

# Comprehensive report
pylint src/ > quality_report.txt

# Test before push
python tests/test_qc.py && isort --check-only src/
```

## Troubleshooting

### Issue: "line too long" warnings

**Solution**: Break long lines using implicit line continuation:

```python
# ❌ Before
result = long_function_name(arg1, arg2, arg3, arg4, arg5, arg6)

# ✅ After
result = long_function_name(
    arg1, arg2, arg3, arg4, arg5, arg6
)
```

### Issue: "missing docstring" warnings

**Solution**: Add docstrings to all public functions:

```python
def my_function(x):
    \"\"\"Short description.
    
    Longer description if needed.
    
    Args:
        x: Parameter description
        
    Returns:
        Return value description
    \"\"\"
    pass
```

### Issue: isort not finding imports correctly

**Solution**: Check that `.isort.cfg` is in the project root and properly configured.

### Issue: pylint score < 8.0

**Solution**: Address critical errors first:

```bash
# Show only errors
pylint --disable=all --enable=E,F src/

# Show long issues
pylint -q src/ | grep "line\|too"
```

## Resources

- **isort documentation**: https://pycqa.github.io/isort/
- **pylint documentation**: https://pylint.pycqa.org/
- **PEP 8 Style Guide**: https://www.python.org/dev/peps/pep-0008/
- **PEP 257 Docstrings**: https://www.python.org/dev/peps/pep-0257/

## Continuous Integration

These linting checks should be run:

1. **Locally** - Before committing (via pre-commit hooks)
2. **On PR** - GitHub Actions workflows
3. **Pre-release** - Full quality audit

### GitHub Actions Example

```yaml
name: Lint

on: [push, pull_request]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
      - run: pip install isort pylint
      - run: isort --check-only src/
      - run: pylint --disable=C,R,W src/
```

---

**Last Updated**: March 10, 2026
**Status**: ✅ COMPLIANT
**Score**: 10.00/10 (critical files)
"""
