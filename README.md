# structa🪵
A lightweight Python library that transforms 
unstructed log data into structured data,
this can be ran locally, as a kubernetes sidecar 
or run as a service to parse logs for Data Engineering
processes.

## Install

```shell
uv pip install .  # or via pip/pipx/poetry.
```

## Quick Start

1. Define your log structure in YAML:

```shell
structa sample > sample_logs.yaml
```

2. Parse logs with one command:

```shell
structa parse --structure <structure>.yaml --input <file_name> --format json
```

## Python API

```python
from structa import LogParser, StructureDefinition

# Parse logs with just three lines of code
structure = StructureDefinition.from_file("<structure>.yaml")
parser = LogParser(structure)
structured_data = parser.parse_file("<file>.log")
```