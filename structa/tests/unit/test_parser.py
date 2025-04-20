"""Unit tests for the LogParser class."""

import pytest
from structa.parser import LogParser
from structa.structure import StructureDefinition


@pytest.mark.unit
def test_parse_line(common_yaml_structure):
    """Test that LogParser can successfully parse a line with a matching pattern."""
    structure_def = StructureDefinition(yaml_content=common_yaml_structure)
    parser = LogParser(structure_def)
    
    log_line = "2023-01-01 12:34:56 INFO This is a test message"
    result = parser.parse_line(log_line)
    
    assert result is not None
    assert result["_pattern"] == "standard_log"
    assert result["timestamp"] == "2023-01-01 12:34:56"
    assert result["level"] == "INFO"
    assert result["message"] == "This is a test message"
    
    non_matching_line = "This doesn't match our pattern"
    result = parser.parse_line(non_matching_line)
    assert result is None


@pytest.mark.unit
def test_convert_value():
    """Test the type conversion logic for different field types."""
    yaml_content = """
    name: TypeConversionTest
    version: "1.0"
    patterns:
      - name: test_pattern
        regex: '(?P<int_val>\\d+),(?P<float_val>\\d+\\.\\d+),(?P<bool_val>true|false),(?P<string_val>\\w+)'
        fields:
          - name: int_val
            type: int
          - name: float_val
            type: float
          - name: bool_val
            type: bool
          - name: string_val
            type: string
    """
    
    structure_def = StructureDefinition(yaml_content=yaml_content)
    parser = LogParser(structure_def)
    
    log_line = "123,45.67,true,hello"
    result = parser.parse_line(log_line)
    
    assert result is not None
    assert result["int_val"] == 123
    assert isinstance(result["int_val"], int)
    
    assert result["float_val"] == 45.67
    assert isinstance(result["float_val"], float)
    
    assert result["bool_val"] is True
    assert isinstance(result["bool_val"], bool)
    
    assert result["string_val"] == "hello"
    assert isinstance(result["string_val"], str) 