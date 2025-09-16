import fitz
import os
import base64
from difflib import SequenceMatcher


def remove_headers_footers(page_texts):
    """
    Remove common headers and footers from page texts

    Args:
        page_texts (list): List of text content from each page

    Returns:
        list: List of cleaned page texts with headers/footers removed
    """
    if len(page_texts) < 2:
        return page_texts

    # Split each page into lines
    page_lines = [text.split('\n') for text in page_texts]

    # Find common header lines across all pages
    header_candidates = []
    max_header_lines = 5

    # Check each potential header line position across all pages
    for line_pos in range(max_header_lines):
        line_content_map = {}  # Map line content to count

        # Collect all different lines at this position from all pages
        for lines in page_lines:
            if line_pos < len(lines):
                line = lines[line_pos].strip()
                if line and len(line) > 3:  # Skip empty or very short lines
                    line_content_map[line] = line_content_map.get(line, 0) + 1

        # Find lines that appear frequently across pages
        for line_content, count in line_content_map.items():
            if count >= len(page_texts) * 0.6:  # Appears in at least 60% of pages
                # Mark this line position as having a header
                header_candidates.append(line_pos)
                break

    # Find common footer lines across all pages
    footer_candidates = []
    max_footer_lines = 5

    # For each page, check the last few lines for common patterns
    for line_pos_from_end in range(1, max_footer_lines + 1):
        line_content_map = {}  # Map line content to count

        # Collect all different lines at this position from all pages
        for lines in page_lines:
            if line_pos_from_end <= len(lines):
                actual_pos = len(lines) - line_pos_from_end
                line = lines[actual_pos].strip()
                if line and len(line) > 3:  # Skip empty or very short lines
                    line_content_map[line] = line_content_map.get(line, 0) + 1

        # Find lines that appear frequently across pages
        for line_content, count in line_content_map.items():
            if count >= len(page_texts) * 0.6:  # Appears in at least 60% of pages
                # Mark this relative position as having a footer
                footer_candidates.append(line_pos_from_end)
                break

    # Clean each page
    cleaned_pages = []
    for lines in page_lines:
        filtered_lines = []

        for i, line in enumerate(lines):
            line = line.strip()
            if not line:  # Keep empty lines for structure
                filtered_lines.append(line)
                continue

            # Skip header lines
            is_header = False
            for header_pos in header_candidates:
                if i == header_pos:
                    is_header = True
                    break

            # Skip footer lines
            is_footer = False
            for footer_pos in footer_candidates:
                if i == len(lines) - footer_pos:
                    is_footer = True
                    break

            if not is_header and not is_footer:
                filtered_lines.append(line)

        # Join lines back and clean up
        cleaned_text = '\n'.join(filtered_lines)
        cleaned_pages.append(cleaned_text)

    return cleaned_pages


def extract_images_as_base64(doc, output_dir="images"):
    """
    Extract images from PDF and convert to base64 for embedding in markdown

    Args:
        doc: fitz document object
        output_dir (str): Directory to save extracted images (optional)

    Returns:
        list: List of tuples (page_num, image_index, base64_data, image_info)
    """
    images = []

    # Create output directory if specified
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for page_num in range(len(doc)):
        page = doc[page_num]
        image_list = page.get_images()

        for img_index, img in enumerate(image_list):
            # Get image data
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]

            # Get image info
            image_info = {
                'width': base_image.get('width', 0),
                'height': base_image.get('height', 0),
                'format': base_image.get('ext', 'png'),
                'size': len(image_bytes)
            }

            # Convert to base64
            base64_data = base64.b64encode(image_bytes).decode('utf-8')

            # Save to file if output_dir specified
            if output_dir:
                image_filename = f"{output_dir}/page_{page_num + 1}_img_{img_index + 1}.{image_info['format']}"
                with open(image_filename, 'wb') as f:
                    f.write(image_bytes)

            images.append((page_num, img_index, base64_data, image_info))

    return images


def pdf_to_markdown(pdf_path, extract_images=True, output_dir="images"):
    """
    Convert PDF file to Markdown format using fitz (PyMuPDF)

    Args:
        pdf_path (str): Path to the PDF file
        extract_images (bool): Whether to extract and embed images
        output_dir (str): Directory to save extracted images

    Returns:
        str: Markdown content extracted from the PDF
    """
    # Check if file exists
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    # Check if file is a PDF
    if not pdf_path.lower().endswith('.pdf'):
        raise ValueError("File must be a PDF file")

    # Open the PDF file
    doc = fitz.open(pdf_path)

    # Extract images if requested
    images = []
    if extract_images:
        images = extract_images_as_base64(doc, output_dir)

    # Extract text from all pages first
    page_texts = []
    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text()
        page_texts.append(text)

    # Remove headers and footers
    cleaned_texts = remove_headers_footers(page_texts)

    # Build markdown content
    markdown_content = ""
    for page_num, text in enumerate(cleaned_texts):
        # Add page separator for better readability
        if page_num > 0:
            markdown_content += "\n\n---\n\n"

        # Add page number as heading
        markdown_content += f"## Page {page_num + 1}\n\n"

        # Add images for this page
        if extract_images:
            page_images = [img for img in images if img[0] == page_num]
            for img_idx, (_, _, base64_data, image_info) in enumerate(page_images):
                # Create markdown image tag with base64 data
                image_markdown = f"![Image {img_idx + 1} - Page {page_num + 1}](data:image/{image_info['format']};base64,{base64_data[:100]}...)"
                markdown_content += image_markdown + "\n\n"

        # Add the cleaned text
        markdown_content += text

    # Close the document
    doc.close()

    return markdown_content


if __name__ == "__main__":
    # Example usage
    import sys
    import argparse

    parser = argparse.ArgumentParser(description='Convert PDF to Markdown with optional image extraction')
    parser.add_argument('pdf_path', help='Path to the PDF file')
    parser.add_argument('output_file', nargs='?', help='Output file path (optional)')
    parser.add_argument('--no-images', action='store_true', help='Disable image extraction')
    parser.add_argument('--image-dir', default='images', help='Directory to save extracted images (default: images)')

    args = parser.parse_args()

    try:
        markdown_content = pdf_to_markdown(args.pdf_path, extract_images=not args.no_images, output_dir=args.image_dir)

        if args.output_file:
            # Write to file
            with open(args.output_file, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            print(f"Markdown content has been written to: {args.output_file}")
        else:
            # Print to stdout
            print(markdown_content)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)