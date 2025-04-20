# Structa Destinations

Structa provides a modular destination system that allows you to export parsed logs to various storage targets. 
This document covers the available destinations, how to use them via both the SDK and CLI, and how to extend 
the system with your own custom destinations.

## Available Destinations

Currently, Structa supports the following destinations:

- **FileSystem**: Write data to the local file system (default)
- **Google Cloud Storage (GCS)**: Store data in Google Cloud Storage buckets
- **BigQuery**: Load data directly into Google BigQuery tables

## Using Destinations in the SDK

### Creating Destinations

The `create_destination()` factory function provides a simple way to create a destination instance:

```python
from structa.destinations import create_destination

# Create a filesystem destination (default)
fs_dest = create_destination("filesystem", 
                            file_system_path="/path/to/output")

# Create a GCS destination
gcs_dest = create_destination("gcs",
                             bucket_name="my-bucket",
                             project_id="my-project",
                             credentials_path="/path/to/credentials.json")

# Create a BigQuery destination
bq_dest = create_destination("bigquery",
                            project_id="my-project",
                            dataset_id="my_dataset",
                            credentials_path="/path/to/credentials.json")
```

### Writing Data to Destinations

All destinations implement the `AbstractDestination` interface, which provides a consistent API:

```python
from structa.structure import StructureDefinition
from structa.parser import LogParser
from structa.destinations import create_destination

# Parse log data
structure_def = StructureDefinition.from_file("structure.yaml")
parser = LogParser(structure_def)
parsed_data = parser.parse_file("logs.txt")

# Create a destination
dest = create_destination("gcs", 
                         bucket_name="my-bucket",
                         project_id="my-project")

# Method 1: Manual connect/write/close
if dest.connect():
    dest.write(parsed_data, "output.json", format="json", pretty=True)
    dest.close()

# Method 2: Using context manager (recommended)
with create_destination("bigquery",
                       project_id="my-project",
                       dataset_id="my_dataset") as dest:
    dest.write(parsed_data, "my_table", format="json")
```

### Destination-Specific Options

#### FileSystem

```python
fs_dest = create_destination(
    "filesystem",
    file_system_alias="local",  # Alias name (default: "local")
    file_system_type="local",   # Type (default: "local")
    file_system_path="/path/to/output",  # Output directory
    file_system_options={
        # Additional options
    }
)

# Write options
fs_dest.write(
    data,
    path="output.json",  # Filename relative to file_system_path
    format="json",       # "json", "csv", or "txt"
    pretty=True          # For JSON formatting
)
```

#### Google Cloud Storage (GCS)

```python
gcs_dest = create_destination(
    "gcs",
    bucket_name="my-bucket",  # Required
    project_id="my-project",  # Optional if in credentials
    credentials_path="/path/to/credentials.json",  # Optional
    options={
        "create_bucket": False,  # Create bucket if doesn't exist
        # Additional client options
    }
)

# Write options
gcs_dest.write(
    data,
    path="path/in/bucket/output.json",  # Path within bucket
    format="json",        # "json", "csv", or "txt"
    pretty=True,          # For JSON formatting
    content_type="application/json"  # Optional MIME type
)
```

#### BigQuery

```python
bq_dest = create_destination(
    "bigquery",
    project_id="my-project",  # Required
    dataset_id="my_dataset",  # Required
    credentials_path="/path/to/credentials.json",  # Optional
    options={
        "create_dataset": False,  # Create dataset if doesn't exist
        "location": "US"  # Dataset location
    }
)

# Write options
bq_dest.write(
    data,
    path="table_name",  # Table name within dataset
    format="json",      # Only used for schema inference
    schema=None,        # Optional schema definition
    write_disposition="WRITE_APPEND",  # WRITE_TRUNCATE, WRITE_APPEND, WRITE_EMPTY
    create_if_missing=True,  # Create table if it doesn't exist
    time_partitioning={
        "type": "DAY",
        "field": "timestamp"
    }
)
```

## Using Destinations in the CLI

The CLI supports all destinations, with `filesystem` as the default. You can specify a different destination
using the `--destination-type` option.

### Basic Usage

```bash
# Default behavior - use filesystem and output to stdout
structa parse -s structure.yaml -i logs.txt

# Write to a file with filesystem destination (default)
structa parse -s structure.yaml -i logs.txt -o output.json -f json

# Use GCS destination 
structa parse -s structure.yaml -i logs.txt --destination-type gcs --destination-config gcs_config.json

# Use BigQuery destination
structa parse -s structure.yaml -i logs.txt --destination-type bigquery --destination-config bq_config.json
```

### Destination Configuration Files

The `--destination-config` option allows you to provide a JSON file with destination-specific options:

#### GCS Configuration (gcs_config.json)

```json
{
  "bucket_name": "my-bucket",
  "project_id": "my-project", 
  "credentials_path": "/path/to/credentials.json",
  "options": {
    "create_bucket": false
  }
}
```

#### BigQuery Configuration (bq_config.json)

```json
{
  "project_id": "my-project",
  "dataset_id": "my_dataset",
  "credentials_path": "/path/to/credentials.json",
  "options": {
    "create_dataset": true,
    "location": "US"
  }
}
```

### Output Format Options

The `--format` option works with all destinations:

```bash
# Output as CSV to BigQuery
structa parse -s structure.yaml -i logs.txt --destination-type bigquery \
              --destination-config bq_config.json -f csv

# Output as pretty JSON to GCS
structa parse -s structure.yaml -i logs.txt --destination-type gcs \
              --destination-config gcs_config.json -f json --pretty
```

## Creating Custom Destinations

You can create your own destination by following these steps:

1. Create a new class that inherits from `AbstractDestination`
2. Implement the required methods: `connect()`, `write()`, and `close()`
3. Add your destination to the factory in `destinations/__init__.py`

### Example: Custom S3 Destination

```python
from typing import Any, Dict, Optional
import json
import io
import csv

from structa.destinations.abstract_destination import AbstractDestination

class S3Destination(AbstractDestination):
    """Destination for writing data to Amazon S3."""
    
    def __init__(self, 
                 bucket_name: str,
                 aws_access_key_id: Optional[str] = None,
                 aws_secret_access_key: Optional[str] = None,
                 region_name: Optional[str] = 'us-east-1',
                 options: Optional[Dict[str, Any]] = None):
        """Initialize S3 destination."""
        self.bucket_name = bucket_name
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.region_name = region_name
        self.options = options or {}
        self.client = None
        self._connected = False
    
    def connect(self) -> bool:
        """Connect to S3."""
        try:
            # Using lazy import to avoid requiring boto3
            import boto3
            
            self.client = boto3.client(
                's3',
                aws_access_key_id=self.aws_access_key_id,
                aws_secret_access_key=self.aws_secret_access_key,
                region_name=self.region_name
            )
            
            # Check if bucket exists
            try:
                self.client.head_bucket(Bucket=self.bucket_name)
            except Exception:
                if self.options.get("create_bucket", False):
                    self.client.create_bucket(Bucket=self.bucket_name)
                else:
                    raise ValueError(f"Bucket {self.bucket_name} does not exist")
                    
            self._connected = True
            return True
        except ImportError:
            print("Error: boto3 package not installed.")
            print("Install with: pip install boto3")
            return False
        except Exception as e:
            print(f"Error connecting to S3: {str(e)}")
            return False
    
    def write(self, data: Any, path: str, **kwargs) -> bool:
        """Write data to S3."""
        if not self._connected:
            if not self.connect():
                return False
                
        format_type = kwargs.get("format", "json").lower()
        pretty = kwargs.get("pretty", True)
        content_type = kwargs.get("content_type", None)
        
        try:
            if format_type == "json":
                if pretty:
                    body = json.dumps(data, indent=2)
                else:
                    body = json.dumps(data)
                content_type = "application/json"
            elif format_type == "csv":
                if not isinstance(data, list):
                    raise ValueError("CSV format requires data to be a list of dictionaries")
                
                csv_buffer = io.StringIO()
                if data:
                    fieldnames = set()
                    for item in data:
                        if isinstance(item, dict):
                            fieldnames.update(item.keys())
                    writer = csv.DictWriter(csv_buffer, fieldnames=list(fieldnames))
                    writer.writeheader()
                    writer.writerows(data)
                    
                body = csv_buffer.getvalue()
                content_type = "text/csv"
            elif format_type == "txt":
                body = str(data)
                content_type = "text/plain"
            else:
                raise ValueError(f"Unsupported format: {format_type}")
                
            # Upload to S3
            self.client.put_object(
                Bucket=self.bucket_name,
                Key=path,
                Body=body,
                ContentType=content_type or "application/octet-stream"
            )
                
            return True
        except Exception as e:
            print(f"Error writing to S3: {str(e)}")
            return False
    
    def close(self) -> None:
        """Close the S3 client."""
        self.client = None
        self._connected = False
```

### Adding to the Factory

Update the `create_destination()` function in `destinations/__init__.py`:

```python
def create_destination(
    destination_type: str,
    **kwargs
) -> AbstractDestination:
    """Factory function to create a destination instance."""
    if destination_type.lower() == 'filesystem':
        from structa.destinations.filesystem import FileSystemDestination
        return FileSystemDestination(...)
    elif destination_type.lower() == 'gcs':
        from structa.destinations.gcs import GCSDestination
        return GCSDestination(...)
    elif destination_type.lower() == 'bigquery':
        from structa.destinations.bigquery import BigQueryDestination
        return BigQueryDestination(...)
    elif destination_type.lower() == 's3':
        from structa.destinations.s3 import S3Destination
        return S3Destination(
            bucket_name=kwargs.get('bucket_name'),
            aws_access_key_id=kwargs.get('aws_access_key_id'),
            aws_secret_access_key=kwargs.get('aws_secret_access_key'),
            region_name=kwargs.get('region_name', 'us-east-1'),
            options=kwargs.get('options')
        )
    else:
        raise ValueError(f"Unsupported destination type: {destination_type}") 