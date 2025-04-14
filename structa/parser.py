"""Module for parsing log files based on structure definitions."""

import re
from typing import Dict, List, Any, Union, Optional, Iterator, TextIO
from pathlib import Path
import regex
from structa.structure import StructureDefinition
from structa.patterns import PatternParser


class LogParser:
    """Parser for log files based on structure definitions."""
    
    def __init__(self, structure_def: StructureDefinition):
        """Initialize with a structure definition.
        
        Args:
            structure_def: StructureDefinition instance
        """
        self.structure_def = structure_def
        self._compiled_patterns = self._compile_patterns()
    
    def _compile_patterns(self) -> List[Dict[str, Any]]:
        """Compile patterns from the structure definition."""
        compiled_patterns = []
        
        for pattern in self.structure_def.patterns:
            pattern_type = pattern.get("type", "regex")  
            pattern_str = pattern["pattern"]
            
            parser = PatternParser.create(pattern_type)
            compiled_pattern = parser.compile(pattern_str)
            
            compiled_patterns.append({
                "pattern": compiled_pattern,
                "parser": parser,
                "fields": pattern["fields"],
                "name": pattern.get("name", "unnamed_pattern"),
                "type": pattern_type
            })
        
        return compiled_patterns
    
    def parse_line(self, line: str) -> Optional[Dict[str, Any]]:
        """Parse a single log line."""
        for pattern in self._compiled_patterns:
            match_dict = pattern["parser"].match(pattern["pattern"], line)
            
            if match_dict:
                result = {
                    "_pattern": pattern["name"]
                }
                
                for field_name, value in match_dict.items():
                    field_def = next((f for f in pattern["fields"] if f["name"] == field_name), None)
                    
                    if field_def:
                        field_type = field_def.get("type", "string")
                        result[field_name] = self._convert_value(value, field_type)
                    else:
                        result[field_name] = value
                        
                return result
        
        return None
    
    def _convert_value(self, value: str, field_type: str) -> Any:
        """Convert a string value to the specified type.
        
        Args:
            value: String value to convert
            field_type: Type to convert to
            
        Returns:
            Converted value
        """
        if field_type == "string":
            return value
        elif field_type == "int":
            try:
                return int(value)
            except ValueError:
                return value
        elif field_type == "float":
            try:
                return float(value)
            except ValueError:
                return value
        elif field_type == "bool":
            if value.lower() in ["true", "yes", "1"]:
                return True
            elif value.lower() in ["false", "no", "0"]:
                return False
            else:
                return value
        else:
            return value
    
    def parse_file(self, file_path: Union[str, Path]) -> List[Dict[str, Any]]:
        """Parse a log file.
        
        Args:
            file_path: Path to the log file
            
        Returns:
            List of dictionaries with parsed fields
        """
        results = []
        path = Path(file_path)
        
        with open(path, 'r') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                    
                parsed_line = self.parse_line(line)
                if parsed_line:
                    results.append(parsed_line)
        
        return results
    
    def parse_text(self, text: str) -> List[Dict[str, Any]]:
        """Parse a text string of log data.
        
        Args:
            text: Log data as a string
            
        Returns:
            List of dictionaries with parsed fields
        """
        results = []
        
        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue
                
            parsed_line = self.parse_line(line)
            if parsed_line:
                results.append(parsed_line)
        
        return results
    
    def parse_stream(self, stream: TextIO) -> Iterator[Dict[str, Any]]:
        """Parse a stream of log data.
        
        Args:
            stream: File-like object to read from
            
        Yields:
            Dictionaries with parsed fields
        """
        for line in stream:
            line = line.strip()
            if not line:
                continue
                
            parsed_line = self.parse_line(line)
            if parsed_line:
                yield parsed_line 