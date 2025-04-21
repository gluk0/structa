from typing import Any, Dict, Optional, List, Union
import json
import tempfile
import csv
import io
import uuid

from structa.destinations.abstract_destination import AbstractDestination

class BigQueryDestination(AbstractDestination):
    """Destination for writing data to Google BigQuery."""
    
    def __init__(self, 
                 project_id: str,
                 dataset_id: str,
                 credentials_path: Optional[str] = None,
                 options: Optional[Dict[str, Any]] = None):
        """Initialize a BigQuery destination.
        
        Args:
            project_id: The GCP project ID
            dataset_id: The BigQuery dataset ID
            credentials_path: Path to service account credentials file
            options: Additional options for the BigQuery client and jobs
        """
        self.project_id = project_id
        self.dataset_id = dataset_id
        self.credentials_path = credentials_path
        self.options = options or {}
        self.client = None
        self.dataset_ref = None
        self._connected = False
    
    def connect(self) -> bool:
        """Connect to BigQuery and validate the dataset exists."""
        try:
            # Using lazy import to avoid requiring google-cloud-bigquery
            # if the destination is not used......
            from google.cloud import bigquery
            from google.oauth2 import service_account
            
            if self.credentials_path:
                credentials = service_account.Credentials.from_service_account_file(
                    self.credentials_path
                )
                self.client = bigquery.Client(
                    project=self.project_id,
                    credentials=credentials
                )
            else:
                self.client = bigquery.Client(project=self.project_id)
            
            dataset_ref = self.client.dataset(self.dataset_id)
            try:
                self.client.get_dataset(dataset_ref)
            except Exception:
                if self.options.get("create_dataset", False):
                    dataset = bigquery.Dataset(dataset_ref)
                    location = self.options.get("location", "europe-west2")
                    dataset.location = location
                    self.client.create_dataset(dataset)
                else:
                    raise ValueError(f"Dataset {self.dataset_id} does not exist in project {self.project_id}")
            
            self.dataset_ref = dataset_ref
            self._connected = True
            return True
        except ImportError:
            print("Error: google-cloud-bigquery package not installed.")
            print("Install with: pip install google-cloud-bigquery")
            return False
        except Exception as e:
            print(f"Error connecting to BigQuery: {str(e)}")
            return False
    
    def write(self, data: Any, path: str, **kwargs) -> bool:
        """Write data to Google BigQuery.
        
        Args:
            data: The data to write (list of records)
            path: The table name or table_id to write to
            **kwargs: Additional options like:
                     - schema: BigQuery schema definition (list of SchemaField objects or dict)
                     - write_disposition: 'WRITE_TRUNCATE', 'WRITE_APPEND', or 'WRITE_EMPTY'
                     - create_if_missing: Create table if it doesn't exist (default: True)
                     - time_partitioning: Time partitioning configuration
        
        Returns:
            bool: Success status
        """
        if not self._connected:
            if not self.connect():
                return False
                
        if not isinstance(data, list):
            raise ValueError("BigQuery destination requires data as a list of records")
            
        if not data:
            print("Warning: Empty data, nothing to write to BigQuery")
            return True
            
        write_disposition = kwargs.get("write_disposition", "WRITE_APPEND")
        create_if_missing = kwargs.get("create_if_missing", True)
        schema = kwargs.get("schema", None)
        time_partitioning = kwargs.get("time_partitioning", None)
        
        try:
            # Using lazy import to avoid requiring google-cloud-bigquery
            from google.cloud import bigquery
            table_ref = self.dataset_ref.table(path)
            table_exists = True
            try:
                self.client.get_table(table_ref)
            except Exception:
                table_exists = False
                
            if not table_exists and create_if_missing:
                if schema is None:
                    schema = self._infer_schema_from_data(data)
                    
                table = bigquery.Table(table_ref, schema=schema)
                
                if time_partitioning:
                    table.time_partitioning = bigquery.TimePartitioning(
                        type_=time_partitioning.get("type", "DAY"),
                        field=time_partitioning.get("field")
                    )
                    
                self.client.create_table(table)
            
            job_config = bigquery.LoadJobConfig()
            
            if schema:
                job_config.schema = schema
                
            if write_disposition:
                job_config.write_disposition = write_disposition
                
            with tempfile.NamedTemporaryFile(mode="w+", suffix=".json") as temp_file:
                for record in data:
                    temp_file.write(json.dumps(record) + "\n")
                temp_file.flush()
                
                with open(temp_file.name, "rb") as source_file:
                    load_job = self.client.load_table_from_file(
                        source_file,
                        table_ref,
                        job_config=job_config
                    )
                    
                # Wait for the job to complete
                load_job.result()
                
            return True
        except Exception as e:
            print(f"Error writing to BigQuery: {str(e)}")
            return False
            
    def _infer_schema_from_data(self, data: List[Dict]):
        """Infer BigQuery schema from data."""
        from google.cloud import bigquery
        
        if not data:
            return []
    
        record = data[0]
        schema = []
        
        for field_name, value in record.items():
            field_type = self._get_bq_field_type(value)
            schema.append(bigquery.SchemaField(field_name, field_type))
            
        return schema
        
    def _get_bq_field_type(self, value: Any) -> str:
        """Convert Python type to BigQuery data type."""
        if isinstance(value, bool):
            return "BOOLEAN"
        elif isinstance(value, int):
            return "INTEGER"
        elif isinstance(value, float):
            return "FLOAT"
        elif isinstance(value, dict):
            return "RECORD"
        elif isinstance(value, (list, tuple)):
            if value and isinstance(value[0], dict):
                return "RECORD"
            return "STRING"  # Convert lists to JSON strings
        else:
            return "STRING"
    
    def close(self) -> None:
        """Close the BigQuery client."""
        if self.client:
            self.client.close()
        self.client = None
        self._connected = False
