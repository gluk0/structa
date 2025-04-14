"""Module for formatting parsed log data into different output formats."""

import json
import csv
from typing import Dict, List, Any, TextIO, Optional, Union
from pathlib import Path


class OutputFormatter:
    """Formatter for parsed log data."""
    
    @staticmethod
    def to_json(data: List[Dict[str, Any]], 
                pretty: bool = False) -> str:
        """Convert parsed data to JSON string.
        
        Args:
            data: List of dictionaries with parsed data
            pretty: Whether to format with indentation
            
        Returns:
            JSON string representation
        """
        if pretty:
            return json.dumps(data, indent=2)
        else:
            return json.dumps(data)
    
    @staticmethod
    def to_csv(data: List[Dict[str, Any]]) -> str:
        """Convert parsed data to CSV string.
        
        Args:
            data: List of dictionaries with parsed data
            
        Returns:
            CSV string representation
        """
        if not data:
            return ""
            
        field_names = set()
        for record in data:
            field_names.update(record.keys())
        
        field_names = sorted(list(field_names))
        
        output = []
        output.append(",".join(field_names))
        
        for record in data:
            row = []
            for field in field_names:
                value = record.get(field, "")
                if isinstance(value, str):
                    if "," in value or '"' in value:
                        value = '"' + value.replace('"', '""') + '"'
                    row.append(str(value))
                else:
                    row.append(str(value))
            output.append(",".join(row))
        
        return "\n".join(output)
    
    @staticmethod
    def to_table(data: List[Dict[str, Any]]) -> str:
        """Convert parsed data to a simple ASCII table.
        
        Args:
            data: List of dictionaries with parsed data
            
        Returns:
            ASCII table representation
        """
        if not data:
            return ""
            
        field_names = set()
        for record in data:
            field_names.update(record.keys())
        
        field_names = sorted(list(field_names))
        
        col_widths = {field: len(field) for field in field_names}
        for record in data:
            for field in field_names:
                value = record.get(field, "")
                col_widths[field] = max(col_widths[field], len(str(value)))
        
        output = []
        
        header = " | ".join(f"{field:{col_widths[field]}}" for field in field_names)
        output.append(header)
        
        separator = "-+-".join("-" * col_widths[field] for field in field_names)
        output.append(separator)
        
        for record in data:
            row = " | ".join(
                f"{str(record.get(field, '')):{col_widths[field]}}" 
                for field in field_names
            )
            output.append(row)
        
        return "\n".join(output)
    
    @staticmethod
    def save_json(data: List[Dict[str, Any]], 
                 file_path: Union[str, Path], 
                 pretty: bool = True) -> None:
        """Save parsed data to a JSON file.
        
        Args:
            data: List of dictionaries with parsed data
            file_path: Path to the output file
            pretty: Whether to format with indentation
        """
        path = Path(file_path)
        with open(path, 'w') as f:
            json.dump(data, f, indent=2 if pretty else None)
    
    @staticmethod
    def save_csv(data: List[Dict[str, Any]], 
                file_path: Union[str, Path]) -> None:
        """Save parsed data to a CSV file.
        
        Args:
            data: List of dictionaries with parsed data
            file_path: Path to the output file
        """
        if not data:
            with open(file_path, 'w') as f:
                f.write("")
            return
            
        path = Path(file_path)
        
        field_names = set()
        for record in data:
            field_names.update(record.keys())
        
        field_names = sorted(list(field_names))
        
        with open(path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=field_names)
            writer.writeheader()
            writer.writerows(data) 