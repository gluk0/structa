from structa.patterns import PatternParser
from typing import Dict, Any, Optional, List
import regex
import string

class TemplatePatternParser(PatternParser):
    """Parser for string template patterns."""
    
    def _template_to_regex(self, pattern: str) -> str:
        """Convert a template pattern to regex."""
        parts = []
        current = 0
        
        placeholders = regex.finditer(r'\{([a-zA-Z0-9_]+)\}', pattern)
        
        for match in placeholders:
            parts.append(regex.escape(pattern[current:match.start()]))
            
            field = match.group(1)
            if field == '_':
                parts.append(r'.+?')
            else:
                parts.append(f'(?P<{field}>.+?)')
            
            current = match.end()
            
        parts.append(regex.escape(pattern[current:]))
        
        return ''.join(parts)
    
    def compile(self, pattern: str) -> Any:
        """Compile the template pattern."""
        regex_pattern = self._template_to_regex(pattern)
        return regex.compile(regex_pattern)
    
    def match(self, compiled_pattern: Any, line: str) -> Optional[Dict[str, str]]:
        """Match a line against the compiled pattern."""
        match = compiled_pattern.match(line)
        if match:
            return match.groupdict()
        return None 