"""Command-line interface for the Structa library."""

import sys
import click
import json
from pathlib import Path
from typing import Optional, TextIO, Dict, Any
import regex
import yaml

from structa.structure import StructureDefinition
from structa.parser import LogParser
from structa.output import OutputFormatter
from structa.utils.banner import get_banner
from structa.destinations import create_destination

@click.group()
def cli():
    """Command-line interface for Structa - a library for parsing log files.
    
    Structa supports multiple pattern formats:
    - regex: Standard regular expressions with named capture groups
    - grok: Simplified patterns based on Logstash/Elasticsearch Grok
    - template: Human-readable string templates with {field} placeholders
    
    Use the appropriate subcommand for your task.
    """
    pass


@cli.command()
@click.option(
    "--structure", "-s", 
    required=True,
    type=click.Path(exists=True, dir_okay=False, readable=True),
    help="Path to the YAML structure definition file."
)
@click.option(
    "--input", "-i",
    required=True,
    type=click.Path(exists=True, dir_okay=False, readable=True),
    help="Path to the log file to parse."
)
@click.option(
    "--output", "-o",
    type=click.Path(dir_okay=False, writable=True),
    help="Path to the output file. If not provided, output to stdout."
)
@click.option(
    "--format", "-f",
    type=click.Choice(["json", "csv", "table"]),
    default="json",
    help="Output format (default: json)."
)
@click.option(
    "--destination-type",
    type=click.Choice(["filesystem", "gcs", "bigquery"]),
    default="filesystem",
    help="Type of destination to write data to (default: filesystem)."
)
@click.option(
    "--destination-config",
    type=click.Path(exists=True, dir_okay=False, readable=True),
    help="Path to a JSON config file for the destination."
)
@click.option(
    "--pretty/--no-pretty",
    default=True,
    help="Use pretty formatting for JSON output (default: pretty)."
)
@click.option(
    "--pattern-format",
    type=click.Choice(["auto", "regex", "grok", "template"]),
    default="auto",
    help="Pattern format to use (default: auto-detect)."
)
def parse(structure, input, output, format, destination_type, destination_config, pretty, pattern_format):
    """Parse a log file according to a structure definition."""
    try:
        structure_def = StructureDefinition.from_file(structure)
        
        if pattern_format != "auto":
            for pattern in structure_def.definition["patterns"]:
                pattern["type"] = pattern_format

        parser = LogParser(structure_def)
        
        parsed_data = parser.parse_file(input)
        
        # Handle the different destination types
        if destination_type != "filesystem" or (output and not output.startswith("-")):
            # Load destination config if provided
            destination_kwargs = {}
            if destination_config:
                with open(destination_config, 'r') as f:
                    destination_kwargs = json.load(f)
            
            # Add relevant CLI options to the destination kwargs
            if destination_type == "filesystem" and output:
                # Use the output path as the file_system_path if it's a directory
                output_path = Path(output)
                if output_path.is_dir():
                    destination_kwargs["file_system_path"] = str(output_path)
                    
                    # Use the input filename as the output filename
                    input_filename = Path(input).name
                    output = str(output_path / input_filename)
                    
                    # Adjust extension based on format if needed
                    if not output.endswith(f".{format}"):
                        output = f"{output}.{format}"
            
            # Create the destination
            dest = create_destination(destination_type, **destination_kwargs)
            
            # Format the data
            if format == "json":
                result_data = parsed_data
                dest.write(
                    result_data, 
                    path=output or Path(input).with_suffix(f".{format}").name,
                    format="json",
                    pretty=pretty
                )
            elif format == "csv":
                result_data = parsed_data
                dest.write(
                    result_data,
                    path=output or Path(input).with_suffix(f".{format}").name,
                    format="csv"
                )
            elif format == "table":
                # Table format is only for display, write as JSON
                result_data = parsed_data
                dest.write(
                    result_data,
                    path=output or Path(input).with_suffix(".json").name,
                    format="json",
                    pretty=pretty
                )
                # Also display the table to stdout
                result = OutputFormatter.to_table(parsed_data)
                click.echo(result)
            else:
                result_data = parsed_data
                dest.write(
                    result_data,
                    path=output or Path(input).with_suffix(".json").name,
                    format="json",
                    pretty=pretty
                )
        else:
            # Legacy behavior - output to stdout or file directly
            if format == "json":
                result = OutputFormatter.to_json(parsed_data, pretty=pretty)
            elif format == "csv":
                result = OutputFormatter.to_csv(parsed_data)
            elif format == "table":
                result = OutputFormatter.to_table(parsed_data)
            else:
                result = OutputFormatter.to_json(parsed_data, pretty=pretty)
            
            if output:
                with open(output, 'w') as f:
                    f.write(result)
            else:
                click.echo(result)
            
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
@click.option(
    "--structure", "-s", 
    required=True,
    type=click.Path(exists=True, dir_okay=False, readable=True),
    help="Path to the YAML structure definition file."
)
def validate(structure):
    """Validate a structure definition file."""
    try:
        structure_def = StructureDefinition.from_file(structure)
        click.echo(f"Structure definition '{structure_def.name}' (v{structure_def.version}) is valid.")
        click.echo(f"Contains {len(structure_def.patterns)} pattern(s).")
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
@click.option(
    "--type", "-t",
    type=click.Choice(["regex", "grok", "template"]),
    default="template",
    help="Pattern type to generate (default: template)."
)
def sample(type):
    """Generate a sample structure definition for the specified pattern type."""
    if type == "regex":
        sample_yaml = """
name: apache_access_log
version: 1.0
description: Structure definition for Apache access logs
patterns:
  - name: common_log_format
    type: regex
    pattern: '^(?P<ip>\\S+) \\S+ (?P<user>\\S+) \\[(?P<timestamp>[^\\]]+)\\] "(?P<method>\\S+) (?P<path>\\S+) (?P<protocol>\\S+)" (?P<status>\\d+) (?P<size>\\d+)$'
    fields:
      - name: ip
        type: string
        description: Client IP address
      - name: user
        type: string
        description: Remote user
"""
    elif type == "grok":
        sample_yaml = """
name: apache_access_log
version: 1.0
description: Structure definition for Apache access logs
patterns:
  - name: common_log_format
    type: grok
    pattern: '%{IP:ip} %{WORD:ident} %{WORD:user} \\[%{TIMESTAMP:timestamp}\\] "%{WORD:method} %{URIPATHPARAM:path} %{WORD:protocol}" %{NUMBER:status} %{NUMBER:size}'
    fields:
      - name: ip
        type: string
        description: Client IP address
      - name: user
        type: string
        description: Remote user
"""
    elif type == "template":
        sample_yaml = """
name: apache_access_log
version: 1.0
description: Structure definition for Apache access logs
patterns:
  - name: common_log_format
    type: template
    pattern: '{ip} {_} {user} [{timestamp}] "{method} {path} {protocol}" {status} {size}'
    fields:
      - name: ip
        type: string
        description: Client IP address
      - name: user
        type: string
        description: Remote user
"""
    
    click.echo(sample_yaml)


@cli.command()
@click.option(
    "--output", "-o",
    type=click.Path(dir_okay=False, writable=True),
    help="Path to save the generated structure definition."
)
@click.option(
    "--format", "-f",
    type=click.Choice(["regex", "grok", "template"]),
    default="template",
    help="Pattern format to generate (default: template)."
)
def build_pattern(output, format):
    """Interactive CLI tool to build a pattern from sample log lines."""
    click.echo("Welcome to the Structa Visual Pattern Builder!")
    click.echo("This tool will help you create a structure definition from sample log lines.")
    
    name = click.prompt("Enter a name for your structure definition")
    version = click.prompt("Enter a version", default="1.0")
    description = click.prompt("Enter a description")
    
    click.echo("\nPlease paste a sample log line:")
    sample = click.prompt("")
    
    click.echo("\nPosition: " + "".join([str(i % 10) for i in range(len(sample))]))
    click.echo("Sample:   " + sample)
    
    fields = []
    patterns = []
    
    if format == "template":
        template_parts = []
        current_pos = 0
        
        while current_pos < len(sample):
            click.echo(f"\nCurrent position: {current_pos}")
            
            next_chars = sample[current_pos:current_pos+10] + "..." if current_pos+10 < len(sample) else sample[current_pos:]
            click.echo(f"Next characters: {next_chars}")
            
            action = click.prompt(
                "What to do?",
                type=click.Choice(["capture", "skip", "literal"]),
                default="capture"
            )
            
            if action == "capture":
                field_name = click.prompt("Field name")
                field_type = click.prompt(
                    "Field type",
                    type=click.Choice(["string", "int", "float", "bool"]),
                    default="string"
                )
                end_pos = click.prompt("End position (exclusive)", type=int)
                
                template_parts.append(f"{{{field_name}}}")
                fields.append({
                    "name": field_name,
                    "type": field_type,
                    "description": f"Extracted from positions {current_pos}-{end_pos}"
                })
                
                current_pos = end_pos
                
            elif action == "skip":
                end_pos = click.prompt("End position (exclusive)", type=int)
                template_parts.append("{_}")
                current_pos = end_pos
                
            elif action == "literal":
                end_pos = click.prompt("End position (exclusive)", type=int)
                literal = sample[current_pos:end_pos]
                template_parts.append(literal)
                current_pos = end_pos
        
        pattern = "".join(template_parts)
        
    elif format == "grok":
        click.echo("\nCommon Grok patterns:")
        click.echo("  %{IP:field}         - IP address")
        click.echo("  %{WORD:field}       - Word")
        click.echo("  %{NUMBER:field}     - Number")
        click.echo("  %{TIMESTAMP:field}  - Timestamp")
        
        pattern = click.prompt("\nEnter a Grok pattern for this log line")
        
        grok_fields = regex.findall(r'%{[A-Z0-9_]+:([a-z0-9_]+)}', pattern)
        
        for field_name in grok_fields:
            field_type = click.prompt(
                f"Type for field '{field_name}'",
                type=click.Choice(["string", "int", "float", "bool"]),
                default="string"
            )
            fields.append({
                "name": field_name,
                "type": field_type
            })
    
    else:  
        pattern = click.prompt(
            "\nEnter a regular expression with named capture groups (?P<name>...)",
            default="^.*$"
        )
        
        regex_fields = regex.findall(r'\(\?P<([a-zA-Z0-9_]+)>', pattern)
        
        for field_name in regex_fields:
            field_type = click.prompt(
                f"Type for field '{field_name}'",
                type=click.Choice(["string", "int", "float", "bool"]),
                default="string"
            )
            fields.append({
                "name": field_name,
                "type": field_type
            })
    
    pattern_def = {
        "name": f"{name}_pattern",
        "type": format,
        "pattern": pattern,
        "fields": fields
    }
    
    structure_def = {
        "name": name,
        "version": version,
        "description": description,
        "patterns": [pattern_def]
    }
    
    yaml_output = yaml.dump(structure_def, sort_keys=False)
    
    if output:
        with open(output, 'w') as f:
            f.write(yaml_output)
        click.echo(f"\nStructure definition saved to {output}")
    else:
        click.echo("\nGenerated structure definition:")
        click.echo(yaml_output)

def main():
    """Main entry point for the CLI."""
    if len(sys.argv) == 1:
        click.echo(get_banner())
        click.echo("Run 'structa --help' for usage information.")
    cli()


if __name__ == "__main__":
    main() 