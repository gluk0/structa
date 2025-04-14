from structa.patterns import PatternParser
from typing import Dict, Any, Optional
import regex
import os
import yaml

class GrokPatternParser(PatternParser):
    """Parser for Grok patterns."""
    
    def __init__(self):
        """Initialize with standard patterns."""
        self.patterns = self._load_patterns()
        
    def _load_patterns(self) -> Dict[str, str]:
        """Load standard Grok patterns."""
        patterns = {
            "IP": r"(?:\d{1,3}\.){3}\d{1,3}",
            "WORD": r"\b\w+\b",
            "NUMBER": r"\d+",
            "TIMESTAMP": r"\d{2}/\w{3}/\d{4}:\d{2}:\d{2}:\d{2} [\+\-]\d{4}",
        }
        
        patterns_path = os.environ.get("STRUCTA_PATTERNS_PATH")
        if patterns_path and os.path.exists(patterns_path):
            with open(patterns_path, 'r') as f:
                custom_patterns = yaml.safe_load(f)
                patterns.update(custom_patterns)
                
        return patterns
    
    def _grok_to_regex(self, pattern: str) -> str:
        """Convert a Grok pattern to regex."""
        grok_regex = r"%{([A-Z0-9_]+):([a-z0-9_]+)}"
        
        def replace_pattern(match):
            pattern_name = match.group(1)
            field_name = match.group(2)
            if pattern_name not in self.patterns:
                raise ValueError(f"Unknown Grok pattern: {pattern_name}")
            return f"(?P<{field_name}>{self.patterns[pattern_name]})"
        
        return regex.sub(grok_regex, replace_pattern, pattern)
    
    def compile(self, pattern: str) -> Any:
        """Compile the Grok pattern."""
        regex_pattern = self._grok_to_regex(pattern)
        return regex.compile(regex_pattern)
    
    def match(self, compiled_pattern: Any, line: str) -> Optional[Dict[str, str]]:
        """Match a line against the compiled pattern."""
        match = compiled_pattern.match(line)
        if match:
            return match.groupdict()
        return None 