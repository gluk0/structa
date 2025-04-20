from typing import Any, Dict, Optional
import json
import io
import tempfile
import csv

from structa.destinations.abstract_destination import AbstractDestination

class GCSDestination(AbstractDestination):
    """Destination for writing data to Google Cloud Storage."""
    
    def __init__(self, 
                 bucket_name: str, 
                 project_id: Optional[str] = None, 
                 credentials_path: Optional[str] = None, 
                 options: Optional[Dict[str, Any]] = None):
        """Initialize a GCS destination.
        
        Args:
            bucket_name: The GCS bucket name
            project_id: The GCP project ID (optional if credentials contain it)
            credentials_path: Path to service account credentials file
            options: Additional options for the GCS client
        """
        self.bucket_name = bucket_name
        self.project_id = project_id
        self.credentials_path = credentials_path
        self.options = options or {}
        self.client = None
        self.bucket = None
        self._connected = False
    
    def connect(self) -> bool:
        """Connect to GCS and validate the bucket exists."""
        try:
            # Using lazy import to avoid requiring google-cloud-storage
            # if the destination is not used
            from google.cloud import storage
            from google.oauth2 import service_account
            
            if self.credentials_path:
                credentials = service_account.Credentials.from_service_account_file(
                    self.credentials_path
                )
                if self.project_id:
                    self.client = storage.Client(
                        project=self.project_id,
                        credentials=credentials
                    )
                else:
                    self.client = storage.Client(credentials=credentials)
            else:
                if self.project_id:
                    self.client = storage.Client(project=self.project_id)
                else:
                    self.client = storage.Client()
                    
            # Check if bucket exists
            self.bucket = self.client.bucket(self.bucket_name)
            if not self.bucket.exists():
                if self.options.get("create_bucket", False):
                    self.bucket.create()
                else:
                    raise ValueError(f"Bucket {self.bucket_name} does not exist")
                    
            self._connected = True
            return True
        except ImportError:
            print("Error: google-cloud-storage package not installed.")
            print("Install with: pip install google-cloud-storage")
            return False
        except Exception as e:
            print(f"Error connecting to GCS: {str(e)}")
            return False
    
    def write(self, data: Any, path: str, **kwargs) -> bool:
        """Write data to Google Cloud Storage.
        
        Args:
            data: The data to write
            path: The blob path within the bucket
            **kwargs: Additional options like:
                     - format: 'json', 'csv', or 'txt'
                     - pretty: boolean for JSON formatting
                     - content_type: MIME type
        
        Returns:
            bool: Success status
        """
        if not self._connected:
            if not self.connect():
                return False
                
        format_type = kwargs.get("format", "json").lower()
        pretty = kwargs.get("pretty", True)
        content_type = kwargs.get("content_type", None)
        
        try:
            blob = self.bucket.blob(path)
            
            if content_type:
                blob.content_type = content_type
                
            if format_type == "json":
                if pretty:
                    json_data = json.dumps(data, indent=2)
                else:
                    json_data = json.dumps(data)
                blob.upload_from_string(json_data, content_type="application/json")
            
            elif format_type == "csv":
                if not isinstance(data, list):
                    raise ValueError("CSV format requires data to be a list of dictionaries")
                
                # Write CSV to in-memory file then upload
                with io.StringIO() as csv_file:
                    if data:
                        fieldnames = set()
                        for item in data:
                            if isinstance(item, dict):
                                fieldnames.update(item.keys())
                        writer = csv.DictWriter(csv_file, fieldnames=list(fieldnames))
                        writer.writeheader()
                        writer.writerows(data)
                        
                    blob.upload_from_string(csv_file.getvalue(), content_type="text/csv")
            
            elif format_type == "txt":
                blob.upload_from_string(str(data), content_type="text/plain")
                
            else:
                raise ValueError(f"Unsupported format: {format_type}")
                
            return True
        except Exception as e:
            print(f"Error writing to GCS: {str(e)}")
            return False
    
    def close(self) -> None:
        """Close the GCS client."""
        self.client = None
        self.bucket = None
        self._connected = False
