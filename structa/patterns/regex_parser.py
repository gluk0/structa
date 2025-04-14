from structa.patterns import PatternParser
from typing import Dict, Any, Optional
import regex

class RegexPatternParser(PatternParser):
    """Parser for regex patterns."""
    
    def compile(self, pattern: str) -> Any:
        """Compile the regex pattern."""
        return regex.compile(pattern)
    
    def match(self, compiled_pattern: Any, line: str) -> Optional[Dict[str, str]]:
        """Match a line against the compiled pattern."""
        match = compiled_pattern.match(line)
        if match:
            return match.groupdict()
        return None 