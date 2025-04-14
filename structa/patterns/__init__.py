from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
import regex

class PatternParser(ABC):
    """Base class for pattern parsers."""
    
    @abstractmethod
    def compile(self, pattern: str) -> Any:
        """Compile the pattern."""
        pass
    
    @abstractmethod
    def match(self, compiled_pattern: Any, line: str) -> Optional[Dict[str, str]]:
        """Match a line against the compiled pattern."""
        pass

    @classmethod
    def create(cls, pattern_type: str):
        """Factory method to create appropriate pattern parser."""
        if pattern_type == "regex":
            from structa.patterns.regex_parser import RegexPatternParser
            return RegexPatternParser()
        elif pattern_type == "grok":
            from structa.patterns.grok_parser import GrokPatternParser
            return GrokPatternParser()
        elif pattern_type == "template":
            from structa.patterns.template_parser import TemplatePatternParser
            return TemplatePatternParser()
        else:
            raise ValueError(f"Unsupported pattern type: {pattern_type}") 