"""Destinations module for writing structured data to various targets."""

from typing import Dict, Any, Optional, Union

from structa.destinations.abstract_destination import AbstractDestination

def create_destination(
    destination_type: str,
    **kwargs
) -> AbstractDestination:
    """Factory function to create a destination instance. Like an Airflow DAG factory! (Made one of these once...)
    
    Args:
        destination_type: Type of destination to create ('filesystem', 'gcs', 'bigquery')
        **kwargs: Configuration options for the specific destination
        
    Returns:
        An initialized destination instance
        
    Raises:
        ValueError: If the destination type is not supported
    """
    if destination_type.lower() == 'filesystem':
        from structa.destinations.filesystem import FileSystemDestination
        return FileSystemDestination(
            file_system_alias=kwargs.get('file_system_alias', 'local'),
            file_system_type=kwargs.get('file_system_type', 'local'),
            file_system_path=kwargs.get('file_system_path', '/tmp'),
            file_system_options=kwargs.get('file_system_options')
        )
    elif destination_type.lower() == 'gcs':
        from structa.destinations.gcs import GCSDestination
        return GCSDestination(
            bucket_name=kwargs.get('bucket_name'),
            project_id=kwargs.get('project_id'),
            credentials_path=kwargs.get('credentials_path'),
            options=kwargs.get('options')
        )
    elif destination_type.lower() == 'bigquery':
        from structa.destinations.bigquery import BigQueryDestination
        return BigQueryDestination(
            project_id=kwargs.get('project_id'),
            dataset_id=kwargs.get('dataset_id'),
            credentials_path=kwargs.get('credentials_path'),
            options=kwargs.get('options')
        )
    else:
        raise ValueError(f"Unsupported destination type: {destination_type}")

# Export the destination classes for direct imports
from structa.destinations.abstract_destination import AbstractDestination
from structa.destinations.filesystem import FileSystemDestination 