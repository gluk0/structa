import os
from typing import Any, Dict, Optional, Union
from pathlib import Path
import json
import csv

from structa.destinations.abstract_destination import AbstractDestination


class FileSystemDestination(AbstractDestination):
    """ FileSystemDestination is class for writing structured data to the file system """ 
    def __init__(self, file_system_alias: str = "local", file_system_type: str = "local", file_system_path: str = "/tmp", file_system_options: Optional[Dict[str, Any]] = None):
        self.file_system_alias = file_system_alias
        self.file_system_type = file_system_type
        self.file_system_path = file_system_path
        self.file_system_options = file_system_options or {}
        self.file_system_client = None
        self._connected = False

    def _validate_options(self):
        """ Validate the file system options """
        if not isinstance(self.file_system_options, dict):
            raise ValueError("file_system_options must be a dictionary")
        # Add any other validation logic here

    def connect(self) -> bool:
        """Connect to the filesystem by ensuring the path exists."""
        try:
            self._validate_options()
            if self.file_system_type == "local":
                # Ensure the directory exists
                path = Path(self.file_system_path)
                path.mkdir(parents=True, exist_ok=True)
                self._connected = True
                return True
            else:
                raise ValueError(f"Unsupported file system type: {self.file_system_type}")
        except Exception as e:
            print(f"Error connecting to filesystem: {str(e)}")
            return False

    def write(self, data: Any, path: str, **kwargs) -> bool:
        """Write data to the filesystem.
        
        Args:
            data: The data to write (list, dict, or str)
            path: Path where data should be written
            **kwargs: Additional options like format (json, csv, txt)
                     pretty (boolean for JSON formatting)
        
        Returns:
            bool: Success status
        """
        if not self._connected:
            if not self.connect():
                return False
                
        format_type = kwargs.get("format", "json").lower()
        pretty = kwargs.get("pretty", True)
        
        try:
            full_path = Path(self.file_system_path) / path
            
            # Create parent directories if they don't exist
            full_path.parent.mkdir(parents=True, exist_ok=True)
                
            if format_type == "json":
                with open(full_path, 'w') as f:
                    if pretty:
                        json.dump(data, f, indent=2)
                    else:
                        json.dump(data, f)
            elif format_type == "csv":
                if not isinstance(data, list):
                    raise ValueError("CSV format requires data to be a list of dictionaries")
                    
                with open(full_path, 'w', newline='') as f:
                    if data:
                        fieldnames = set()
                        for item in data:
                            if isinstance(item, dict):
                                fieldnames.update(item.keys())
                        writer = csv.DictWriter(f, fieldnames=list(fieldnames))
                        writer.writeheader()
                        writer.writerows(data)
            elif format_type == "txt":
                with open(full_path, 'w') as f:
                    f.write(str(data))
            else:
                raise ValueError(f"Unsupported format: {format_type}")
                
            return True
        except Exception as e:
            print(f"Error writing to filesystem: {str(e)}")
            return False

    def close(self) -> None:
        """Close any open resources."""
        self._connected = False
