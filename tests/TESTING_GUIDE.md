"""
Testing Guide for EcoFOCIpy

This document provides instructions for running tests and writing new tests
for the EcoFOCIpy package.

## Quick Start

### Running All Tests

    python -m pytest tests/ -v

### Running Specific Test File

    python -m pytest tests/test_qc.py -v

### Running with Coverage

    pip install pytest-cov
    python -m pytest tests/ --cov=EcoFOCIpy --cov-report=html

### Running Specific Test

    python -m pytest tests/test_qc.py::TestRangeCheck::test_all_good_data -v

## Test Structure

Each test file follows this structure:

```python
import unittest
import numpy as np
import pandas as pd

class TestModuleName(unittest.TestCase):
    '''Tests for specific module functionality.'''
    
    def setUp(self):
        '''Set up test fixtures (run before each test).'''
        pass
    
    def tearDown(self):
        '''Clean up after tests (run after each test).'''
        pass
    
    def test_specific_function(self):
        '''Test description - clear and specific.'''
        pass
```

## Writing Good Tests

### Test Naming Conventions

- Test modules: `test_<module_name>.py`
- Test classes: `Test<ClassName>`
- Test methods: `test_<function_or_behavior>`

### Test Structure (AAA Pattern)

Each test should follow Arrange-Act-Assert:

```python
def test_example():
    # ARRANGE: Set up test data
    input_data = np.array([1, 2, 3])
    expected = np.array([2, 4, 6])
    
    # ACT: Call the function
    result = double_values(input_data)
    
    # ASSERT: Check the result
    np.testing.assert_array_equal(result, expected)
```

### Test Data

- Use small datasets (typically < 100 elements)
- Include edge cases (empty, single element, very large/small values)
- Include realistic data when testing algorithms
- Use fixtures for complex setup

### Assertions

Use specific assertions:

```python
# Good
self.assertEqual(value, 5)
np.testing.assert_array_equal(arr1, arr2)
pd.testing.assert_frame_equal(df1, df2)
self.assertRaises(ValueError, function, bad_arg)

# Avoid
self.assertTrue(value == 5)  # Too vague
```

## Current Test Coverage

### Quality Control (QC) Module (`test_qc.py`)

Tests for:
- Range checking (min/max validation)
- Spike detection (statistical outliers)
- Rate of change validation
- Comprehensive QC suite

Coverage:
- Good data detection
- Out-of-range flagging
- NaN/missing value handling
- Pandas Series support
- Custom QC flag values
- Multiple detection methods
- Integration with realistic data

## Running Tests from Command Line

### Install Test Dependencies

    pip install pytest pytest-cov

### Run All Tests

    pytest

### Run with Verbose Output

    pytest -v

### Run Specific Test Class

    pytest tests/test_qc.py::TestRangeCheck -v

### Generate Coverage Report

    pytest --cov=EcoFOCIpy --cov-report=html

Then open `htmlcov/index.html` in a browser.

## Continuous Integration

Tests run automatically on:
- GitHub push events
- Pull requests
- Via GitHub Actions in `.github/workflows/`

See workflow configurations for details.

## Performance Testing

For performance-critical code:

```python
import time

def test_performance():
    data = np.random.randn(1000000)
    
    start = time.perf_counter()
    result = expensive_operation(data)
    elapsed = time.perf_counter() - start
    
    # Should complete in less than 1 second
    self.assertLess(elapsed, 1.0)
```

## Debugging Failed Tests

### Run With Detailed Output

    pytest -vv --tb=long tests/test_qc.py

### Drop into Debugger on Failure

    pytest --pdb tests/test_qc.py

### Print Debug Info

```python
def test_with_debug():
    result = function_under_test()
    print(f"Result type: {type(result)}")
    print(f"Result shape: {result.shape if hasattr(result, 'shape') else 'N/A'}")
    print(f"Result values: {result}")
    assert result is not None
```

## Best Practices

1. **One assertion per test** (when possible)
   - Easier to identify what failed
   - Except for related assertions on same object

2. **Use descriptive test names**
   - What is being tested
   - What conditions
   - What's expected

3. **Keep tests independent**
   - Don't rely on other tests running first
   - Clean up resources in tearDown

4. **Test edge cases**
   - Empty data
   - Single element
   - Very large values
   - NaN/inf/None
   - Type variations (Series vs array)

5. **Use parametrization for multiple inputs**

   ```python
   @pytest.mark.parametrize("input,expected", [
       ([1, 2, 3], [2, 4, 6]),
       ([], []),
       ([0], [0]),
   ])
   def test_double(input, expected):
       assert double_values(input) == expected
   ```

## Adding New Tests

When adding new functionality:

1. Write test FIRST (Test-Driven Development)
2. Test should FAIL initially
3. Implement minimal code to pass test
4. Refactor as needed

Example:

```python
# tests/test_new_feature.py
def test_new_feature():
    '''Test new feature behavior.'''
    result = new_feature(input_data)
    expected_output = some_value
    assert result == expected_output
```

## Coverage Goals

Maintain >80% test coverage for:
- Core functionality (qc, instruments)
- I/O utilities (ncCFsave, parsers)
- Math computations

Coverage reports are generated automatically in CI.

## Troubleshooting

### Test Discovery Issues

Ensure:
- Test files start with `test_`
- Test classes inherit from `unittest.TestCase`
- Test methods start with `test_`
- `__init__.py` exists in test directory

### Import Errors

```python
# Add parent directory to path
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
```

### Fixture Issues

```python
def setUp(self):
    '''Run before each test method.'''
    self.test_data = create_data()

def tearDown(self):
    '''Run after each test method.'''
    if hasattr(self, 'test_data'):
        del self.test_data
```

## Resources

- [Python unittest documentation](https://docs.python.org/3/library/unittest.html)
- [pytest documentation](https://docs.pytest.org/)
- [NumPy testing utilities](https://numpy.org/doc/stable/reference/testing.html)
- [Pandas testing utilities](https://pandas.pydata.org/docs/reference/testing.html)

---

Last Updated: 2026-03-10
"""
