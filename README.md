# structa

```
       _                          _               
  ___ | |_    ____  _   _   ____ | |_    ____     
 /___)|  _)  / ___)| | | | / ___)|  _)  / _  |    
|___ || |__ | |    | |_| |( (___ | |__ ( ( | |    
(___/  \___)|_|     \____| \____) \___) \_||_|    

      chop your logs to structured data                                                
```

A lightweight Python library that transforms unstructured log files into structured data using YAML-defined patterns.

## Install

```shell
uv pip install .  # or pip install .
```

## Quick Start

1. Define your log structure in YAML:

```shell
structa sample > apache_logs.yaml
```

2. Parse logs with one command:

```shell
structa parse --structure apache_logs.yaml --input access.log --format json
```

## Python API

```python
from structa import LogParser, StructureDefinition

# Parse logs with just three lines of code
structure = StructureDefinition.from_file("apache_logs.yaml")
parser = LogParser(structure)
structured_data = parser.parse_file("access.log")
```