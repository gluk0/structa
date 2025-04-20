"""Centralized logging configuration for the structa package."""

import logging
import sys
from typing import Optional


class LoggingConfig:
    """
    Centralized logging configuration for the structa package.
    
    This class provides a consistent logging setup across the application,
    allowing for uniform log formatting and levels.
    """
    
    DEFAULT_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    DEFAULT_LEVEL = logging.INFO
    
    @classmethod
    def get_logger(cls, name: str, 
                  level: Optional[int] = None, 
                  format_string: Optional[str] = None) -> logging.Logger:
        """
        Get a configured logger instance.
        
        Args:
            name: The name of the logger, typically __name__
            level: The logging level (defaults to INFO if not specified)
            format_string: Custom format string (uses default if not specified)
            
        Returns:
            A configured logger instance
        """
        logger = logging.getLogger(name)
        
        # Set the level
        logger.setLevel(level or cls.DEFAULT_LEVEL)
        
        # Only add handler if not already configured
        if not logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            formatter = logging.Formatter(format_string or cls.DEFAULT_FORMAT)
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger


def get_logger(name: str, 
              level: Optional[int] = None, 
              format_string: Optional[str] = None) -> logging.Logger:
    """
    Convenience function to get a configured logger.
    
    Args:
        name: The name of the logger, typically __name__
        level: The logging level (defaults to INFO if not specified)
        format_string: Custom format string (uses default if not specified)
        
    Returns:
        A configured logger instance
    """
    return LoggingConfig.get_logger(name, level, format_string) 