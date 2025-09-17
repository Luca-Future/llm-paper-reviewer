"""
Base classes for file parsers.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from pathlib import Path
import logging

from domain.models.paper import Paper, PaperType
from core.exceptions import PaperParseError


logger = logging.getLogger(__name__)


class BaseParser(ABC):
    """Base class for file parsers."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}

    @abstractmethod
    def can_parse(self, file_path: str) -> bool:
        """Check if parser can handle the file."""
        pass

    @abstractmethod
    async def parse(self, file_path: str, **kwargs) -> Paper:
        """Parse file and return Paper object."""
        pass

    def validate_file(self, file_path: str) -> bool:
        """Validate file exists and is readable."""
        path = Path(file_path)
        return path.exists() and path.is_file()

    def get_file_size(self, file_path: str) -> int:
        """Get file size in bytes."""
        try:
            return Path(file_path).stat().st_size
        except OSError:
            return 0

    def estimate_processing_time(self, file_path: str) -> float:
        """Estimate processing time in seconds."""
        file_size = self.get_file_size(file_path)
        # Simple estimation: 1MB per second
        return max(1.0, file_size / (1024 * 1024))


