# structa Tests

This directory contains the test suite for the structa project.

## Test Structure

- `unit/`: Contains unit tests for individual components
- `integration/`: Contains integration tests for end-to-end functionality

## Running Tests

You can run the tests using pytest. Make sure you have installed the development dependencies:

```bash
# Install dev dependencies
uv pip install -e ".[dev]"
```

### Run all tests

```bash
pytest -v
```

### Run only unit tests

```bash
pytest -v -m unit
```

### Run only integration tests

```bash
pytest -v -m integration
```

### Run tests with coverage

```bash
pytest -v --cov=structa
```

## Adding New Tests

- Unit tests should be placed in the `unit/` directory
- Integration tests should be placed in the `integration/` directory
- Test files should be named with the `test_` prefix
- Add the appropriate marker to your tests:
  - `@pytest.mark.unit` for unit tests
  - `@pytest.mark.integration` for integration tests 