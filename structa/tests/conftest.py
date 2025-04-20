"""Pytest configuration and shared fixtures for structa tests."""

import os
import sys
import pytest
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))


@pytest.fixture
def examples_dir():
    """Return the path to the examples directory."""
    return Path(__file__).parent.parent.parent / "examples"


@pytest.fixture
def common_yaml_structure():
    """Create a common YAML structure definition for testing."""
    return """
    name: TestLogFormat
    version: "1.0"
    patterns:
      - name: standard_log
        regex: '(?P<timestamp>\\d{4}-\\d{2}-\\d{2} \\d{2}:\\d{2}:\\d{2}) (?P<level>\\w+) (?P<message>.*)'
        fields:
          - name: timestamp
            type: string
          - name: level
            type: string
          - name: message
            type: string
    """


@pytest.fixture
def sample_log_lines():
    """Return a list of sample log lines for testing."""
    return [
        "2023-01-01 12:34:56 INFO Starting application",
        "2023-01-01 12:34:57 DEBUG Initializing components",
        "2023-01-01 12:34:58 INFO Components initialized",
        "2023-01-01 12:34:59 WARNING Low memory available",
        "2023-01-01 12:35:00 ERROR Failed to process request: Connection timeout",
        "This line doesn't match the pattern",
        "2023-01-01 12:35:01 INFO Application shutdown"
    ]


@pytest.fixture
def temp_log_file(sample_log_lines):
    """Create a temporary log file with sample log lines for testing."""
    log_content = "\n".join(sample_log_lines)
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp:
        tmp.write(log_content)
        tmp_path = tmp.name
    
    yield tmp_path
    
    os.unlink(tmp_path) 