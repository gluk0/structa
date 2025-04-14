"""Structa - A library for parsing log files into structured data."""

__version__ = "0.1.0"

from structa.parser import LogParser
from structa.structure import StructureDefinition
from structa.output import OutputFormatter

__all__ = ["LogParser", "StructureDefinition", "OutputFormatter"] 