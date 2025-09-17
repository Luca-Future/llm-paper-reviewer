"""
Paper domain model.
"""

import hashlib
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
from enum import Enum


class PaperType(Enum):
    """Paper format types."""
    PDF = "pdf"
    TXT = "txt"
    MD = "md"
    MARKDOWN = "markdown"


@dataclass
class PaperMetadata:
    """Paper metadata."""
    title: Optional[str] = None
    author: Optional[str] = None
    publication_date: Optional[datetime] = None
    doi: Optional[str] = None
    pages: int = 0
    file_size: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class Paper:
    """Paper domain model."""
    id: str
    file_path: str
    content: str
    paper_type: PaperType
    metadata: PaperMetadata = field(default_factory=PaperMetadata)
    extracted_images: List[Dict[str, Any]] = field(default_factory=list)

    def __post_init__(self):
        """Initialize paper after creation."""
        if not self.id:
            self.id = self._generate_id()

        if not self.metadata.title:
            self.metadata.title = self._extract_title_from_content()

        # Update file size
        try:
            self.metadata.file_size = Path(self.file_path).stat().st_size
        except (OSError, FileNotFoundError):
            pass

    def _generate_id(self) -> str:
        """Generate unique ID for the paper."""
        content_hash = hashlib.md5(self.content.encode()).hexdigest()
        return f"paper_{content_hash[:16]}"

    def _extract_title_from_content(self) -> Optional[str]:
        """Extract title from paper content."""
        lines = self.content.split('\n')
        for line in lines[:10]:  # Check first 10 lines
            line = line.strip()
            if line.startswith('# '):
                return line[2:].strip()
            elif line and not line.startswith('#') and len(line) < 100:
                # Consider as potential title if it's a short line without markdown
                return line
        return None

    def get_word_count(self) -> int:
        """Get word count of the paper content."""
        return len(self.content.split())

    def get_reading_time(self, words_per_minute: int = 250) -> int:
        """Estimate reading time in minutes."""
        return max(1, self.get_word_count() // words_per_minute)

    def to_dict(self) -> Dict[str, Any]:
        """Convert paper to dictionary."""
        return {
            'id': self.id,
            'file_path': self.file_path,
            'content': self.content,
            'paper_type': self.paper_type.value,
            'metadata': {
                'title': self.metadata.title,
                'author': self.metadata.author,
                'publication_date': self.metadata.publication_date.isoformat() if self.metadata.publication_date else None,
                'doi': self.metadata.doi,
                'pages': self.metadata.pages,
                'file_size': self.metadata.file_size,
                'created_at': self.metadata.created_at.isoformat(),
                'updated_at': self.metadata.updated_at.isoformat()
            },
            'extracted_images': self.extracted_images,
            'word_count': self.get_word_count(),
            'reading_time': self.get_reading_time()
        }

    @classmethod
    def from_file(cls, file_path: str) -> 'Paper':
        """Create paper from file."""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Paper file not found: {file_path}")

        # Determine paper type
        extension = path.suffix.lower().lstrip('.')
        try:
            paper_type = PaperType(extension)
        except ValueError:
            raise ValueError(f"Unsupported file type: {extension}")

        # Read content
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()

        return cls(
            id="",  # Will be generated in __post_init__
            file_path=str(path.absolute()),
            content=content,
            paper_type=paper_type
        )