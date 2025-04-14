#!/usr/bin/env python3
"""Structa usage for historical logs"""

import os
import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).parent.parent))

from structa.structure import StructureDefinition
from structa.parser import LogParser
from structa.output import OutputFormatter


def main():
    """Run the example script."""
    script_dir = Path(__file__).parent
    
    structure_file = script_dir / "apache_logs.yaml"
    print(f"Loading structure definition from {structure_file}")
    structure = StructureDefinition.from_file(structure_file)
    
    print(f"Loaded structure definition: {structure.name} (v{structure.version})")
    print(f"Number of patterns: {len(structure.patterns)}")
    
    parser = LogParser(structure)
    
    log_file = script_dir / "sample_access.log"
    print(f"\nParsing log file: {log_file}")
    parsed_data = parser.parse_file(log_file)
    
    print(f"Successfully parsed {len(parsed_data)} log entries")
    
    print("\nJSON Output (first 2 entries):")
    json_output = OutputFormatter.to_json(parsed_data[:2], pretty=True)
    print(json_output)
    
    print("\nCSV Output (first 5 entries):")
    csv_output = OutputFormatter.to_csv(parsed_data[:5])
    print(csv_output)
    
    print("\nTable Output (first 3 entries):")
    table_output = OutputFormatter.to_table(parsed_data[:3])
    print(table_output)
    
    output_dir = script_dir / "output"
    output_dir.mkdir(exist_ok=True)
    
    json_file = output_dir / "parsed_logs.json"
    print(f"\nSaving all entries as JSON to {json_file}")
    OutputFormatter.save_json(parsed_data, json_file)
    
    csv_file = output_dir / "parsed_logs.csv"
    print(f"Saving all entries as CSV to {csv_file}")
    OutputFormatter.save_csv(parsed_data, csv_file)
    
    print("\nExample completed successfully!")


if __name__ == "__main__":
    main() 