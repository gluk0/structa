"""Module for handling structure definitions in YAML format."""

import yaml
from typing import Dict, List, Any, Optional
from pathlib import Path


class StructureDefinition:
    """Handles log structure definitions in YAML format."""
    
    def __init__(self, yaml_content: Optional[str] = None, yaml_file: Optional[Path] = None):
        """Initialize from YAML string or file.
        
        Args:
            yaml_content: YAML structure definition string
            yaml_file: Path to a YAML structure definition file
            
        Raises:
            ValueError: If neither yaml_content nor yaml_file is provided
        """
        if yaml_content is None and yaml_file is None:
            raise ValueError("Either yaml_content or yaml_file must be provided")
            
        if yaml_file is not None:
            with open(yaml_file, 'r') as f:
                self.definition = yaml.safe_load(f)
        else:
            self.definition = yaml.safe_load(yaml_content)
            
        self._validate_definition()
    
    def _validate_definition(self) -> None:
        """Validate the structure definition.
        
        Raises:
            ValueError: If the definition is invalid
        """
        if not isinstance(self.definition, dict):
            raise ValueError("Structure definition must be a dictionary")
            
        required_keys = ["name", "version", "patterns"]
        for key in required_keys:
            if key not in self.definition:
                raise ValueError(f"Structure definition must contain a '{key}' key")
                
        if not isinstance(self.definition["patterns"], list):
            raise ValueError("The 'patterns' key must contain a list of pattern definitions")
            
        for i, pattern in enumerate(self.definition["patterns"]):
            if not isinstance(pattern, dict):
                raise ValueError(f"Pattern at index {i} must be a dictionary")
                
            if "regex" not in pattern and "pattern" not in pattern:
                raise ValueError(f"Pattern at index {i} must contain either a 'regex' or 'pattern' key")
                
            if "fields" not in pattern:
                raise ValueError(f"Pattern at index {i} must contain a 'fields' key")
                
            if not isinstance(pattern["fields"], list):
                raise ValueError(f"'fields' in pattern at index {i} must be a list")
    
    @property
    def name(self) -> str:
        """Get the name of the structure definition."""
        return self.definition["name"]
    
    @property
    def version(self) -> str:
        """Get the version of the structure definition."""
        return self.definition["version"]
    
    @property
    def patterns(self) -> List[Dict[str, Any]]:
        """Get the list of patterns in the structure definition."""
        return self.definition["patterns"]
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get the metadata of the structure definition."""
        metadata = {k: v for k, v in self.definition.items() if k not in ["patterns"]}
        return metadata
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the structure definition to a dictionary."""
        return self.definition
    
    @classmethod
    def from_file(cls, file_path: str) -> "StructureDefinition":
        """Create a StructureDefinition from a YAML file.
        
        Args:
            file_path: Path to a YAML file
            
        Returns:
            A new StructureDefinition instance
        """
        return cls(yaml_file=Path(file_path)) 