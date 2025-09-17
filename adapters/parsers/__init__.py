"""
Parser adapters for different file formats.
"""

from .base import BaseParser
from .pdf_parser import PDFParser
from .text_parser import TextParser
from .registry import ParserRegistry

__all__ = ['BaseParser', 'PDFParser', 'TextParser', 'ParserRegistry']