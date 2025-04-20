from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Union, BinaryIO, TextIO

class AbstractDestination(ABC):
    """Abstract base class for data destinations such as BigQuery, GCS, S3, SFTP, and file systems."""

    @abstractmethod
    def connect(self) -> bool:
        """Establish a connection to the destination.
        
        Returns:
            bool: True if connection was successful, False otherwise.
        """
        pass

    @abstractmethod
    def write(self, data: Any, path: str, **kwargs) -> bool:
        """Write data to the destination.
        
        Args:
            data: The data to write.
            path: Path or identifier for where the data should be written.
            **kwargs: Additional arguments specific to the destination.
            
        Returns:
            bool: True if write was successful, False otherwise.
        """
        pass

    @abstractmethod
    def close(self) -> None:
        """Close the connection to the destination."""
        pass

    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()