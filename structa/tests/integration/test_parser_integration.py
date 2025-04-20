"""Integration tests for the LogParser class."""

import pytest
from pathlib import Path
from structa.parser import LogParser
from structa.structure import StructureDefinition


@pytest.fixture
def log_structure_def(common_yaml_structure):
    """Create a sample structure definition for testing."""
    return StructureDefinition(yaml_content=common_yaml_structure)


@pytest.mark.integration
def test_parse_file_integration(temp_log_file, log_structure_def):
    """Test parsing a log file end-to-end."""
    parser = LogParser(log_structure_def)
    results = parser.parse_file(temp_log_file)
    
    # Should have parsed 6 lines (one line doesn't match)
    assert len(results) == 6
    
    # Check first parsed line
    assert results[0]["_pattern"] == "standard_log"
    assert results[0]["timestamp"] == "2023-01-01 12:34:56"
    assert results[0]["level"] == "INFO"
    assert results[0]["message"] == "Starting application"
    
    # Check last parsed line
    assert results[-1]["_pattern"] == "standard_log"
    assert results[-1]["timestamp"] == "2023-01-01 12:35:01"
    assert results[-1]["level"] == "INFO"
    assert results[-1]["message"] == "Application shutdown"
    
    # Check for error message
    error_entry = next((r for r in results if r["level"] == "ERROR"), None)
    assert error_entry is not None
    assert "Failed to process request" in error_entry["message"]


@pytest.mark.integration
def test_parse_stream_integration(temp_log_file, log_structure_def):
    """Test parsing a log stream end-to-end."""
    parser = LogParser(log_structure_def)
    
    with open(temp_log_file, 'r') as f:
        results = list(parser.parse_stream(f))
    
    # Should have parsed 6 lines (one line doesn't match)
    assert len(results) == 6
    
    # Verify we have all log levels represented
    log_levels = [entry["level"] for entry in results]
    assert "INFO" in log_levels
    assert "DEBUG" in log_levels
    assert "WARNING" in log_levels
    assert "ERROR" in log_levels


@pytest.mark.integration
def test_parse_text_integration(sample_log_lines, log_structure_def):
    """Test parsing text content directly."""
    parser = LogParser(log_structure_def)
    log_text = "\n".join(sample_log_lines)
    
    results = parser.parse_text(log_text)
    
    # Should have parsed 6 lines (one line doesn't match)
    assert len(results) == 6
    
    # Verify all expected log levels are present
    log_levels = set(entry["level"] for entry in results)
    assert log_levels == {"INFO", "DEBUG", "WARNING", "ERROR"} 