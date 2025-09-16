# Paper Reviewer AI

An intelligent academic paper analysis tool that uses AI to automatically summarize and review research papers. Supports both PDF and text files with multilingual analysis capabilities.

## Features

- **AI-Powered Analysis**: Uses OpenAI's language models for deep paper analysis
- **Multi-Format Support**: Handles PDF, TXT, and Markdown files
- **Multilingual**: Supports English and Chinese analysis with language-appropriate outputs
- **Structured Output**: Generates comprehensive analysis including summary, problems, solutions, and limitations
- **Configurable Prompts**: Multiple analysis prompt versions for different needs
- **Image Extraction**: Optional image extraction from PDF files
- **Clean Text Processing**: Intelligent header/footer removal for better analysis quality

## Installation

### Prerequisites

- Python >= 3.11
- uv package manager
- OpenAI API key

### Setup

1. Clone this repository:
```bash
git clone <repository-url>
cd paper-reviewer-ai
```

2. Install dependencies with uv:
```bash
uv sync
```

3. Set up environment variables:
```bash
cp .env.example .env
```

4. Edit `.env` file and add your OpenAI API key:
```bash
OPENAI_API_KEY=your-openai-api-key-here
PROMPT_VERSION=EN  # Options: EN, ZH, EN_2_0, ZH_2_0
```

## Quick Start

### Analyze a Paper

```bash
# Analyze PDF file (automatically converts to markdown)
python paper_analyzer.py paper.pdf

# Analyze text/markdown file
python paper_analyzer.py paper.md

# Save analysis to JSON file
python paper_analyzer.py paper.pdf -o analysis.json

# Use Chinese analysis
python paper_analyzer.py paper.pdf --prompt-version ZH_2_0
```

### PDF to Markdown Conversion

```bash
# Convert PDF to markdown without images
python pdf_parser.py paper.pdf output.md --no-images

# Convert PDF to markdown with images
python pdf_parser.py paper.pdf output.md
```

## Usage Examples

### Basic Analysis
```bash
python paper_analyzer.py research_paper.pdf
```

### Advanced Analysis with Enhanced Prompts
```bash
python paper_analyzer.py research_paper.pdf --prompt-version EN_2_0 -o detailed_analysis.json
```

### Chinese Analysis
```bash
python paper_analyzer.py research_paper.pdf --prompt-version ZH_2_0
```

## Output Format

The analysis generates structured output including:

- **Title**: Paper title
- **Summary**: Comprehensive overview of the paper
- **Problem**: Research questions or challenges addressed
- **Solution**: Methodology and approach used
- **Limitations**: Technical constraints and unresolved issues
- **Key Contributions**: Main contributions to the field
- **Research Significance** (Enhanced version): Impact and importance of the work

## Prompt Versions

### Version 1.0 (Basic)
- **EN/ZH**: Standard 5-field analysis
- Quick overview of paper content

### Version 2.0 (Enhanced)
- **EN_2_0/ZH_2_0**: Enhanced 6-field analysis
- Includes research significance evaluation
- More detailed analysis requirements

## Configuration

### Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key (required)
- `PROMPT_VERSION`: Default prompt version (EN, ZH, EN_2_0, ZH_2_0)
- `OPENAI_MODEL`: Default model (default: gpt-4o)
- `OPENAI_TEMPERATURE`: Response randomness (default: 0.1)

### Command Line Options

```bash
python paper_analyzer.py <input_file> [OPTIONS]

Options:
  --output, -o        Output file path for JSON results
  --model             OpenAI model name (default: gpt-4o)
  --temperature       Response temperature (0-1, default: 0.1)
  --max-length        Maximum characters to analyze (default: 8000)
  --prompt-version    Prompt version (EN, ZH, EN_2_0, ZH_2_0)
```

## File Support

### Input Formats
- **PDF**: Automatic text extraction with header/footer removal
- **TXT**: Plain text files
- **MD/Markdown**: Markdown formatted files

### Output Formats
- **Console**: Formatted text output with section headers
- **JSON**: Structured data for programmatic use

## Architecture

### Core Components

1. **PDF Parser**: Handles PDF to markdown conversion with intelligent text cleaning
2. **Paper Analyzer**: AI analysis engine using LangChain and OpenAI models
3. **Prompt System**: Configurable analysis templates for different languages and versions

### Data Flow

```
Input File -> PDF Parser (if needed) -> Text Processing -> AI Analysis -> Structured Output
```

## Requirements

- Python >= 3.11
- langchain >= 0.3.27
- langchain-openai >= 0.3.33
- pymupdf >= 1.26.4
- python-dotenv >= 1.1.1

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- OpenAI for providing the language models
- LangChain team for the excellent orchestration framework
- PyMuPDF for robust PDF processing capabilities