"""Unit tests for the LogParser class."""

import pytest
from structa.parser import LogParser
from structa.structure import StructureDefinition


def test_parse_line():
    """Test that LogParser can successfully parse a line with a matching pattern."""
    yaml_content = """
    name: TestStructure
    version: "1.0"
    patterns:
      - name: test_pattern
        pattern: "(?P<timestamp>\\d{4}-\\d{2}-\\d{2} \\d{2}:\\d{2}:\\d{2}) (?P<level>\\w+) (?P<message>.*)"
        type: regex
        fields:
          - name: timestamp
            type: string
          - name: level
            type: string
          - name: message
            type: string
    """
    
    structure_def = StructureDefinition(yaml_content=yaml_content)
    parser = LogParser(structure_def)
    
    log_line = "2023-01-01 12:34:56 INFO This is a test message"
    result = parser.parse_line(log_line)
    
    assert result is not None
    assert result["_pattern"] == "test_pattern"
    assert result["timestamp"] == "2023-01-01 12:34:56"
    assert result["level"] == "INFO"
    assert result["message"] == "This is a test message"
    
    non_matching_line = "This doesn't match our pattern"
    result = parser.parse_line(non_matching_line)
    assert result is None 