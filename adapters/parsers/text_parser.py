"""
Text file parser adapter.
"""

import re
import logging
from typing import Optional, Dict, Any, List
from pathlib import Path

from .base import BaseParser
from domain.models.paper import Paper, PaperType
from core.exceptions import PaperParseError


logger = logging.getLogger(__name__)


class TextParser(BaseParser):
    """Text file parser."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.supported_extensions = ['.txt', '.md', '.markdown']

    def can_parse(self, file_path: str) -> bool:
        """Check if parser can handle the file."""
        return Path(file_path).suffix.lower() in self.supported_extensions

    async def parse(self, file_path: str, **kwargs) -> Paper:
        """Parse text file and return Paper object."""
        if not self.validate_file(file_path):
            raise PaperParseError(f"Text file not found or not readable: {file_path}")

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Clean content
            content = self._clean_content(content)

            # Create paper object
            paper = Paper.from_file(file_path)

            logger.info(f"Successfully parsed text file: {file_path}, {len(content)} characters")
            return paper

        except UnicodeDecodeError:
            # Try with different encodings
            try:
                with open(file_path, 'r', encoding='latin-1') as f:
                    content = f.read()

                content = self._clean_content(content)
                paper = Paper.from_file(file_path)

                logger.info(f"Successfully parsed text file with latin-1 encoding: {file_path}")
                return paper

            except Exception as e:
                raise PaperParseError(f"Failed to parse text file {file_path} with encoding issues: {e}")

        except Exception as e:
            logger.error(f"Failed to parse text file {file_path}: {e}")
            raise PaperParseError(f"Failed to parse text file {file_path}: {e}")

    def _clean_content(self, content: str) -> str:
        """Clean and normalize content."""
        # Normalize line endings
        content = content.replace('\r\n', '\n').replace('\r', '\n')

        # Remove excessive empty lines
        content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)

        # Remove leading/trailing whitespace from each line
        lines = [line.rstrip() for line in content.split('\n')]
        content = '\n'.join(lines)

        # Remove leading/trailing whitespace
        content = content.strip()

        return content

    def detect_paper_structure(self, content: str) -> Dict[str, Any]:
        """Detect paper structure in markdown/text content."""
        structure = {
            'has_title': False,
            'has_abstract': False,
            'has_sections': False,
            'has_references': False,
            'sections': [],
            'word_count': 0,
            'reading_time': 0
        }

        lines = content.split('\n')

        # Detect title (first # heading or first non-empty line)
        for line in lines:
            if line.strip():
                if line.startswith('# '):
                    structure['has_title'] = True
                    break
                else:
                    # First non-empty line as title
                    structure['has_title'] = True
                    break

        # Detect sections
        section_pattern = re.compile(r'^#+\s+.+')
        for line in lines:
            if section_pattern.match(line):
                structure['has_sections'] = True
                section_name = re.sub(r'^#+\s+', '', line).strip()
                structure['sections'].append(section_name)

        # Detect abstract
        abstract_keywords = ['abstract', '摘要', 'summary']
        for line in lines:
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in abstract_keywords):
                structure['has_abstract'] = True
                break

        # Detect references
        ref_keywords = ['references', 'bibliography', '参考文献', 'reference']
        for line in lines:
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in ref_keywords):
                structure['has_references'] = True
                break

        # Calculate word count and reading time
        structure['word_count'] = len(content.split())
        structure['reading_time'] = max(1, structure['word_count'] // 250)  # 250 words per minute

        return structure

    def extract_metadata(self, content: str) -> Dict[str, Any]:
        """Extract metadata from text content."""
        metadata = {
            'title': None,
            'authors': [],
            'date': None,
            'keywords': []
        }

        lines = content.split('\n')

        # Extract title (first # heading)
        for line in lines:
            if line.startswith('# '):
                metadata['title'] = line[2:].strip()
                break

        # Look for author information
        author_patterns = [
            r'author[s]?:\s*(.+)',
            r'by\s+(.+)',
            r'作者[：:]\s*(.+)'
        ]

        for line in lines:
            for pattern in author_patterns:
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    authors_text = match.group(1)
                    # Split by common separators
                    authors = re.split(r'[,;]|and|&', authors_text)
                    metadata['authors'] = [author.strip() for author in authors if author.strip()]
                    break

        # Look for date
        date_patterns = [
            r'date:\s*(\d{4}-\d{2}-\d{2})',
            r'(\d{4})\s*年',
            r'published:\s*(\d{4}-\d{2}-\d{2})'
        ]

        for line in lines:
            for pattern in date_patterns:
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    metadata['date'] = match.group(1)
                    break

        return metadata