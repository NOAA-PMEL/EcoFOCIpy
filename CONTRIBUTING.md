"""
Contributing to EcoFOCIpy

Thank you for your interest in contributing to EcoFOCIpy! This document provides
guidelines and instructions for contributing code, documentation, and improvements.

## Getting Started

### Setup Development Environment

1. Fork the repository on GitHub
2. Clone your fork locally:

   ```bash
   git clone https://github.com/<your-username>/EcoFOCIpy.git
   cd EcoFOCIpy
   ```

3. Create a development environment:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\\Scripts\\activate
   pip install -e .
   pip install -r requirements-dev.txt
   ```

4. Create a feature branch:

   ```bash
   git checkout -b feature/your-feature-name
   ```

## Code Standards

### Style Guide

We follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) with these tools:

- **Linting**: `pylint`, `flake8`
- **Formatting**: `black` (line length: 88)
- **Import sorting**: `isort`

Run before committing:

```bash
isort .
black src/ tests/
flake8 src/ tests/
pylint src/EcoFOCIpy/**/*.py
```

### Type Hints

All functions should have type hints (PEP 484):

```python
from typing import Optional, Tuple, Union
import numpy as np
import pandas as pd

def process_data(
    data: Union[pd.Series, np.ndarray],
    threshold: float = 3.0,
    method: Optional[str] = None,
) -> Tuple[np.ndarray, dict]:
    '''
    Process oceanographic data.
    
    Parameters
    ----------
    data : pd.Series or np.ndarray
        Input sensor data.
    threshold : float, optional
        Processing threshold (default: 3.0).
    method : str, optional
        Processing method (default: None).
    
    Returns
    -------
    tuple
        Processed data and metadata dictionary.
    '''
    pass
```

### Docstrings

Use NumPy docstring format:

```python
def function_name(param1: str, param2: int) -> bool:
    '''
    Brief one-line description.
    
    Extended description with more details about what the function does,
    its behavior, and any important notes.
    
    Parameters
    ----------
    param1 : str
        Description of param1.
    param2 : int
        Description of param2, with default or range if applicable.
    
    Returns
    -------
    bool
        Description of return value.
    
    Raises
    ------
    ValueError
        When param1 is invalid.
    TypeError
        When param2 is not an integer.
    
    Examples
    --------
    >>> result = function_name("example", 42)
    >>> print(result)
    True
    
    Notes
    -----
    Additional implementation notes or mathematical background.
    
    References
    ----------
    .. [1] Author et al., "Title", Journal, Year.
    '''
    pass
```

## Making Changes

### Code Changes

1. Make your changes in the appropriate module
2. Add type hints to all functions/methods
3. Add comprehensive docstrings
4. Write tests for new functionality
5. Update relevant documentation

### Testing

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_qc.py -v

# Generate coverage report
pytest --cov=EcoFOCIpy --cov-report=html tests/
```

Tests are required for:
- New functions
- Bug fixes (add regression test)
- Modified functions

### Documentation

- Update docstrings for modified functions
- Add examples in docstrings
- Update README.md if adding features
- Update HISTORY.rst with breaking changes
- Add Jupyter notebook examples for major features

## Commit Guidelines

### Commit Messages

Follow conventional commits format:

```
type(scope): description

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring without functionality change
- `test`: Adding or updating tests
- `perf`: Performance improvement
- `maint`: Maintenance and dependency updates

Examples:

```
feat(qc): add spike detection using MAD method

Add Median Absolute Deviation (MAD) method for robust spike detection
that is less sensitive to outliers than standard deviation.

Fixes #123
```

```
fix(io): handle missing values in NetCDF export

Previously NaN values caused export to fail. Now properly handled
with CF conventions.

Closes #456
```

## Pull Request Process

1. **Before submitting PR**:
   - Run tests: `pytest tests/ -v`
   - Run linter: `flake8 src/ tests/`
   - Format code: `black src/ tests/`

2. **Create PR on GitHub**:
   - Clear title and description
   - Link related issues: "Fixes #123"
   - Reference any breaking changes
   - Include screenshots if UI changes

3. **PR description template**:

   ```markdown
   ## Description
   Brief description of changes.
   
   ## Type of Change
   - [ ] Bug fix
   - [ ] New feature
   - [ ] Breaking change
   - [ ] Documentation
   
   ## Related Issues
   Fixes #123
   
   ## Testing
   - [ ] Added unit tests
   - [ ] Ran full test suite
   - [ ] Tested with realistic data
   
   ## Checklist
   - [ ] Code follows style guidelines
   - [ ] Added docstrings
   - [ ] Updated documentation
   - [ ] Tests pass locally
   - [ ] No new warnings generated
   ```

4. **Address review feedback**
   - Make requested changes
   - Re-run tests
   - Push updates (don't force push on PR)

## Areas for Contribution

### High Priority

- Expanding test coverage (target >85%)
- Documentation improvements
- Bug fixes reported in issues
- Performance optimizations
- New instrument parsers

### Medium Priority

- Code refactoring for maintainability
- Additional examples and notebooks
- I/O format support
- Visualization improvements

### Lower Priority

- Code style improvements
- Comment documentation
- Dependency updates

## Questions?

- **Issues**: Create GitHub issue for bugs/features
- **Discussions**: Use GitHub Discussions for questions
- **Email**: Contact maintainers directly if needed

## Code of Conduct

Be respectful and professional:
- Assume good intentions
- Be constructive with feedback
- Follow all community guidelines
- Report violations to maintainers

## License

By contributing, you agree that your contributions will be licensed under
the same BSD-3-Clause license as the project.

---

Thank you for contributing to EcoFOCIpy!

Last Updated: 2026-03-10
