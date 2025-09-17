"""
Parser registry for managing multiple parsers.
"""

import logging
from typing import List, Optional, Dict, Any
from pathlib import Path

from .base import BaseParser
from domain.models.paper import Paper
from core.exceptions import PaperAnalysisError


logger = logging.getLogger(__name__)


class ParserRegistry:
    """Registry for managing multiple file parsers."""

    def __init__(self):
        self.parsers: List[BaseParser] = []
        self._extension_map: Dict[str, BaseParser] = {}

    def register_parser(self, parser: BaseParser):
        """Register a parser."""
        self.parsers.append(parser)

        # Update extension map
        for ext in parser.supported_extensions:
            self._extension_map[ext.lower()] = parser

        logger.info(f"Registered parser: {parser.__class__.__name__} for extensions: {parser.supported_extensions}")

    def get_parser(self, file_path: str) -> Optional[BaseParser]:
        """Get appropriate parser for file."""
        extension = Path(file_path).suffix.lower()
        parser = self._extension_map.get(extension)

        if parser:
            logger.debug(f"Found parser {parser.__class__.__name__} for {file_path}")
        else:
            logger.warning(f"No parser found for extension: {extension}")

        return parser

    def get_supported_extensions(self) -> List[str]:
        """Get list of all supported file extensions."""
        return list(self._extension_map.keys())

    def get_parser_info(self) -> Dict[str, Any]:
        """Get information about all registered parsers."""
        info = {
            'total_parsers': len(self.parsers),
            'supported_extensions': self.get_supported_extensions(),
            'parsers': []
        }

        for parser in self.parsers:
            parser_info = {
                'name': parser.__class__.__name__,
                'supported_extensions': parser.supported_extensions,
                'config': parser.config
            }
            info['parsers'].append(parser_info)

        return info

    async def parse_file(self, file_path: str, **kwargs) -> Paper:
        """Parse file using appropriate parser."""
        parser = self.get_parser(file_path)
        if not parser:
            raise PaperAnalysisError(f"No parser found for file: {file_path}")

        if not parser.validate_file(file_path):
            raise PaperAnalysisError(f"File not found or not readable: {file_path}")

        try:
            return await parser.parse(file_path, **kwargs)
        except Exception as e:
            logger.error(f"Failed to parse file {file_path}: {e}")
            raise PaperAnalysisError(f"Failed to parse file {file_path}: {e}")

    def can_parse(self, file_path: str) -> bool:
        """Check if any parser can handle the file."""
        return self.get_parser(file_path) is not None