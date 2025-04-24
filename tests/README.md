# Tests Package

This directory contains unit and integration tests for the project.

## Structure

- Each test module should begin with `test_` and correspond to a source module.
- Place common test utilities or fixtures in a `conftest.py` or `utils.py`.

## Running Tests

You can run all tests using:

```bash
uv run unittest discover -s tests
```

Or with `pytest` if preferred:

```bash
pytest tests
```

## Conventions

- Use `unittest.TestCase` or `pytest` style consistently.
- Group related test functions using class-based structure.
- Keep tests isolated and deterministic.
- Mock external dependencies where appropriate.

## Writing New Tests

1. Create a new file named `test_<module_name>.py`.
2. Define a test class that inherits from `unittest.TestCase`.
3. Use meaningful method names like `test_functionality_description`.
4. Assert expected behavior using `self.assertEqual`, `self.assertTrue`, etc.

## Example

```python
import unittest
from my_module import my_function

class TestMyFunction(unittest.TestCase):
    def test_returns_correct_value(self):
        self.assertEqual(my_function(2, 3), 5)
```

## Notes

- All test files should reside in the `tests/` directory.
- Use virtualenv or `uv` to isolate test dependencies.
- Maintain high test coverage for reliability.

---

Feel free to extend this README with any project-specific testing patterns or tools.

