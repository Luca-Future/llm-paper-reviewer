# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Paper Reviewer AI is a Python application that analyzes academic papers using AI. It processes PDF and text files, extracts content, and generates structured analysis using OpenAI's language models. The system supports multiple languages (English/Chinese) and configurable prompt versions.

## Architecture

### Core Components

1. **PDF Parser** (`pdf_parser.py`): Converts PDF to Markdown with header/footer removal and optional image extraction
2. **Paper Analyzer** (`paper_analyzer.py`): Main AI analysis engine using LangChain with OpenAI models
3. **Prompt System** (`prompts/`): Configurable analysis templates with multilingual support

### Data Flow

```
PDF/TXT Input → PDF Parser (if needed) → Text Processing → AI Analysis → Structured Output
```

## Common Commands

### Environment Setup
```bash
# Copy environment configuration
cp .env.example .env
# Edit .env with your OpenAI API key
```

### Basic Usage
```bash
# Analyze PDF file (auto-converts to markdown)
python paper_analyzer.py paper.pdf

# Analyze text/markdown file
python paper_analyzer.py paper.md

# Save analysis to JSON
python paper_analyzer.py paper.pdf -o analysis.json

# Use specific prompt version
python paper_analyzer.py paper.pdf --prompt-version ZH_2_0
```

### PDF Processing
```bash
# Convert PDF to markdown without images
python pdf_parser.py paper.pdf output.md --no-images

# Convert PDF to markdown with images (saves to ./images/)
python pdf_parser.py paper.pdf output.md
```

## Configuration

### Environment Variables
- `OPENAI_API_KEY`: Required for OpenAI model access
- `PROMPT_VERSION`: Sets default prompt version (EN, ZH, EN_2_0, ZH_2_0)

### Prompt Versions
- **EN/ZH**: Basic 5-field analysis (title, summary, problem, solution, limitations, contributions)
- **EN_2_0/ZH_2_0**: Enhanced 6-field analysis adding "research significance"
- Chinese prompts explicitly request Chinese responses

## Technical Architecture

### Key Design Patterns
- **Strategy Pattern**: Prompt version selection via `PromptLoader` class
- **Template Method**: LangChain prompt templating with format instructions
- **Pipeline Pattern**: Sequential processing through PDF parsing → AI analysis → output formatting

### Error Handling
- Graceful degradation when PDF parser unavailable
- File type validation with descriptive error messages
- API error handling with fallback responses

### Multilingual Support
- Dynamic output formatting based on selected prompt version
- Language-specific field names and display formatting
- Chinese prompts enforce Chinese responses from AI models

## Development Notes

### Dependencies
- Python >=3.11
- LangChain (>=0.3.27) for AI orchestration
- PyMuPDF (>=1.26.4) for PDF processing
- Uses Pydantic (not langchain_core.pydantic_v1) for data validation

### File Processing
- Supports: PDF, TXT, MD, MARKDOWN files
- Automatic file type detection
- PDF processing includes intelligent header/footer removal
- Text length limiting to avoid token overflow

### Schema-Based Output
- Dynamic Pydantic model creation from JSON schemas
- Flexible output structures per prompt version
- JSON output with consistent field naming across languages