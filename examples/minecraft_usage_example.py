#!/usr/bin/env python3
"""Structa usage for Minecraft server logs"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from structa.structure import StructureDefinition
from structa.parser import LogParser
from structa.output import OutputFormatter


def main():
    """Run the Minecraft log parsing example script."""
    script_dir = Path(__file__).parent
    
    structure_file = script_dir / "minecraft_logs.yaml"
    print(f"Loading structure definition from {structure_file}")
    structure = StructureDefinition.from_file(structure_file)
    
    print(f"Loaded structure definition: {structure.name} (v{structure.version})")
    print(f"Number of patterns: {len(structure.patterns)}")
    
    parser = LogParser(structure)
    
    log_file = script_dir / "sample_minecraft.log"
    print(f"\nParsing Minecraft log file: {log_file}")
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
    
    json_file = output_dir / "minecraft_logs.json"
    print(f"\nSaving all entries as JSON to {json_file}")
    OutputFormatter.save_json(parsed_data, json_file)
    
    csv_file = output_dir / "minecraft_logs.csv"
    print(f"Saving all entries as CSV to {csv_file}")
    OutputFormatter.save_csv(parsed_data, csv_file)
    
    print("\nFiltering for player connection events:")
    connections = [entry for entry in parsed_data if entry.get('pattern_name') == 'player_connection']
    print(f"Found {len(connections)} player connection events")
    if connections:
        print(OutputFormatter.to_table(connections))
    
    print("\nFiltering for chat messages:")
    chat_messages = [entry for entry in parsed_data if entry.get('pattern_name') == 'chat_message']
    print(f"Found {len(chat_messages)} chat messages")
    if chat_messages:
        print(OutputFormatter.to_table(chat_messages))
    
    print("\nExample completed successfully!")


if __name__ == "__main__":
    main() 