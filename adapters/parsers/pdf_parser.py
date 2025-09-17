"""
PDF file parser adapter.
"""

import fitz  # PyMuPDF
import base64
import re
import logging
from typing import Optional, Dict, Any, List, Tuple
from pathlib import Path
import io

from .base import BaseParser
from domain.models.paper import Paper, PaperType
from core.exceptions import PaperParseError


logger = logging.getLogger(__name__)


class PDFParser(BaseParser):
    """PDF file parser using PyMuPDF."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.supported_extensions = ['.pdf']
        self.max_image_size = 1024 * 1024  # 1MB

    def can_parse(self, file_path: str) -> bool:
        """Check if parser can handle the file."""
        return Path(file_path).suffix.lower() in self.supported_extensions

    async def parse(self, file_path: str, extract_images: bool = False, remove_headers_footers: bool = True) -> Paper:
        """Parse PDF file and return Paper object."""
        if not self.validate_file(file_path):
            raise PaperParseError(f"PDF file not found or not readable: {file_path}")

        try:
            doc = fitz.open(file_path)
            extracted_images = []

            # Extract text from all pages
            page_texts = []
            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text()

                if extract_images:
                    page_images = self._extract_images_from_page(page, page_num)
                    extracted_images.extend(page_images)

                page_texts.append(text)

            # Remove headers and footers if requested
            if remove_headers_footers and len(page_texts) > 2:
                page_texts = self._remove_headers_footers(page_texts)

            # Combine all page texts
            content = "\n\n".join(page_texts)

            # Clean up content
            content = self._clean_content(content)

            paper = Paper.from_file(file_path)
            paper.extracted_images = extracted_images

            logger.info(f"Successfully parsed PDF: {file_path}, {len(content)} characters")
            return paper

        except Exception as e:
            logger.error(f"Failed to parse PDF {file_path}: {e}")
            raise PaperParseError(f"Failed to parse PDF {file_path}: {e}")

    def _extract_images_from_page(self, page, page_num: int) -> List[Dict[str, Any]]:
        """Extract images from PDF page."""
        images = []
        image_list = page.get_images(full=True)

        for img_index, img in enumerate(image_list):
            try:
                # Get image data
                base_image = img[0]
                pix = fitz.Pixmap(page.parent, base_image)

                if pix.n - pix.alpha < 4:  # RGB or GRAY
                    img_data = pix.tobytes("ppm")
                    img_ext = "ppm"
                else:  # RGBA
                    img_data = pix.tobytes("png")
                    img_ext = "png"

                # Check image size
                if len(img_data) > self.max_image_size:
                    logger.warning(f"Image too large, skipping: page {page_num}, image {img_index}")
                    continue

                # Convert to base64
                img_base64 = base64.b64encode(img_data).decode('utf-8')

                images.append({
                    "page": page_num,
                    "index": img_index,
                    "format": img_ext,
                    "size": len(img_data),
                    "data": img_base64
                })

                pix = None  # Free memory

            except Exception as e:
                logger.warning(f"Failed to extract image from page {page_num}, image {img_index}: {e}")
                continue

        return images

    def _remove_headers_footers(self, page_texts: List[str]) -> List[str]:
        """Remove common headers and footers from page texts."""
        if len(page_texts) < 2:
            return page_texts

        # Analyze all pages for common header/footer patterns
        all_lines = []
        for text in page_texts:
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            all_lines.append(lines)

        # Find common patterns that appear on most pages
        line_frequency = {}
        for lines in all_lines:
            for line in lines:
                if len(line) > 5:  # Ignore very short lines
                    line_frequency[line] = line_frequency.get(line, 0) + 1

        # Identify headers/footers (lines that appear on many pages)
        total_pages = len(page_texts)
        header_footer_lines = set()

        for line, freq in line_frequency.items():
            if freq >= total_pages * 0.6:  # Appears on 60% or more pages
                header_footer_lines.add(line)

        # Remove headers/footers from each page
        cleaned_texts = []
        for text in page_texts:
            lines = text.split('\n')
            cleaned_lines = [
                line for line in lines
                if line.strip() not in header_footer_lines
            ]
            cleaned_texts.append('\n'.join(cleaned_lines))

        return cleaned_texts

    def _clean_content(self, content: str) -> str:
        """Clean and normalize content."""
        # Remove excessive whitespace
        content = re.sub(r'\s+', ' ', content)

        # Remove empty lines
        content = '\n'.join(line.strip() for line in content.split('\n') if line.strip())

        # Fix common PDF encoding issues
        content = content.replace('ﬁ', 'fi')
        content = content.replace('ﬂ', 'fl')
        content = content.replace('ﬀ', 'ff')
        content = content.replace('ﬃ', 'ffi')
        content = content.replace('ﬄ', 'ffl')

        return content.strip()

    def get_pdf_info(self, file_path: str) -> Dict[str, Any]:
        """Get PDF metadata information."""
        try:
            doc = fitz.open(file_path)
            metadata = doc.metadata

            return {
                'title': metadata.get('title', ''),
                'author': metadata.get('author', ''),
                'subject': metadata.get('subject', ''),
                'creator': metadata.get('creator', ''),
                'producer': metadata.get('producer', ''),
                'creation_date': metadata.get('creationDate', ''),
                'modification_date': metadata.get('modDate', ''),
                'page_count': len(doc),
                'file_size': self.get_file_size(file_path)
            }
        except Exception as e:
            logger.error(f"Failed to get PDF info for {file_path}: {e}")
            return {}