# Paper Reviewer AI

A modern, modular academic paper analysis tool with a clean architecture using AI to automatically summarize and review research papers. Supports both PDF and text files with multilingual analysis capabilities.

## Features

- **AI-Powered Analysis**: Uses OpenAI's language models for deep paper analysis
- **Multi-Format Support**: Handles PDF, TXT, and Markdown files
- **Multilingual**: Supports English and Chinese analysis with language-appropriate outputs
- **Structured Output**: Generates comprehensive analysis including summary, problems, solutions, and limitations
- **Configurable Prompts**: Multiple analysis prompt versions for different needs
- **Image Extraction**: Optional image extraction from PDF files
- **Clean Text Processing**: Intelligent header/footer removal for better analysis quality
- **Modern Architecture**: Clean layered design with dependency injection
- **CLI Interface**: Full-featured command-line interface with batch processing
- **Extensible Design**: Plugin-based system for adding new features

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
PROMPT_VERSION=EN_2_0  # Options: EN, ZH, EN_2_0, ZH_2_0
AI_PROVIDER=openai
```

5. Verify installation:
```bash
uv run python -m interfaces.cli.main info
```

## Quick Start

### Using the CLI Interface

```bash
# Analyze a single paper
uv run python -m interfaces.cli.main analyze paper.pdf

# Save analysis to JSON file
uv run python -m interfaces.cli.main analyze paper.pdf --output analysis.json

# Use enhanced analysis
uv run python -m interfaces.cli.main analyze paper.pdf --prompt-version EN_2_0

# Get system information
uv run python -m interfaces.cli.main info

# Test AI service connection
uv run python -m interfaces.cli.main test-connection
```

### Batch Processing

```bash
# Analyze all papers in a directory
uv run python -m interfaces.cli.main batch-analyze ./papers --output-dir ./results

# Control concurrency
uv run python -m interfaces.cli.main batch-analyze ./papers --concurrent 2
```

## Usage Examples

### Basic Analysis
```bash
uv run python -m interfaces.cli.main analyze research_paper.pdf --verbose
```

### Advanced Analysis with Enhanced Prompts
```bash
uv run python -m interfaces.cli.main analyze research_paper.pdf --prompt-version EN_2_0 --output detailed_analysis.json
```

### Chinese Analysis
```bash
uv run python -m interfaces.cli.main analyze research_paper.pdf --prompt-version ZH_2_0
```

### Batch Analysis
```bash
uv run python -m interfaces.cli.main batch-analyze ./papers --output-dir ./results --concurrent 3
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
- `AI_PROVIDER`: AI service provider (openai, deepseek)
- `PROMPT_VERSION`: Default prompt version (EN, ZH, EN_2_0, ZH_2_0)
- `OPENAI_MODEL`: Default model (default: gpt-4o)
- `OPENAI_TEMPERATURE`: Response randomness (default: 0.1)
- `MAX_PAPER_LENGTH`: Maximum characters to analyze (default: 128000)

### Command Line Options

```bash
uv run python -m interfaces.cli.main [COMMAND] [OPTIONS]

Commands:
  analyze          Analyze a single paper
  batch-analyze    Analyze multiple papers in a directory
  test-connection  Test connection to AI service
  info             Display system information

Options:
  --input           Input file/directory path
  --output, -o      Output file/directory path
  --model           AI model name
  --prompt-version  Prompt version (EN, ZH, EN_2_0, ZH_2_0)
  --max-length      Maximum characters to analyze
  --concurrent      Number of concurrent analyses (batch)
  --extract-images  Extract images from PDF
  --verbose, -v     Verbose output
```

## Architecture

### Layered Architecture

The project follows a clean layered architecture with dependency injection:

```
┌─────────────────────────────────────────────────────────────┐
│                    Interfaces Layer                         │
│              (CLI, API, Web Interface)                     │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                    Application Layer                        │
│                   (Orchestration, Commands)                │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                      Core Layer                            │
│                 (Analysis Engine, Logic)                   │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                    Domain Layer                            │
│            (Models, Business Rules, Services)              │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                  Adapters Layer                            │
│        (AI Services, Parsers, Storage, External APIs)     │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│              Infrastructure Layer                          │
│           (Configuration, Logging, DI Container)            │
└─────────────────────────────────────────────────────────────┘
```

### Key Components

1. **Dependency Injection Container**: Manages service lifecycle and dependencies
2. **Analysis Orchestrator**: Coordinates analysis with fallback support
3. **AI Adapters**: Pluggable AI service providers (OpenAI, DeepSeek)
4. **Parser Registry**: Extensible file parser system
5. **Domain Models**: Type-safe business entities with validation
6. **Configuration System**: Environment-based configuration with type safety

### Design Patterns

- **Dependency Injection**: For loose coupling and testability
- **Adapter Pattern**: For external service integration
- **Strategy Pattern**: For different analysis strategies
- **Factory Pattern**: For service creation
- **Observer Pattern**: For event handling (future enhancement)

## File Support

### Input Formats
- **PDF**: Automatic text extraction with header/footer removal
- **TXT**: Plain text files
- **MD/Markdown**: Markdown formatted files

### Output Formats
- **Console**: Formatted text output with section headers
- **JSON**: Structured data for programmatic use

## Requirements

The project uses uv for dependency management. All required packages are specified in `pyproject.toml`:

- **Core**: Python >= 3.11, click, pydantic
- **AI**: openai, langchain-core
- **PDF Processing**: pymupdf (fitz)
- **Utilities**: python-dotenv, pyyaml

## Development

### Project Structure

```
paper-reviewer-ai/
├── adapters/           # External service adapters
│   ├── ai/            # AI service providers
│   ├── parsers/       # File parsers
│   └── storage/       # Storage adapters
├── core/              # Core business logic
│   ├── analyzer.py    # Analysis engine
│   └── exceptions.py  # Custom exceptions
├── domain/            # Domain models and services
│   ├── models/        # Business entities
│   └── services/      # Domain services
├── infrastructure/     # Infrastructure concerns
│   ├── config/        # Configuration management
│   └── container.py   # Dependency injection
├── interfaces/        # User interfaces
│   ├── cli/           # Command line interface
│   ├── api/           # REST API
│   └── web/           # Web interface
├── prompts/           # Analysis prompt templates
├── tests/             # Test suite
├── docs/              # Documentation
└── scripts/           # Utility scripts
```

### Adding New Features

1. **New AI Provider**: Add to `adapters/ai/`
2. **New File Format**: Add to `adapters/parsers/`
3. **New Analysis Logic**: Extend core analysis engine
4. **New Commands**: Add to `interfaces/cli/`
5. **Configuration**: Update `infrastructure/config/`

### Testing

```bash
# Run all tests
uv run pytest

# Run specific test categories
uv run pytest tests/unit/
uv run pytest tests/integration/
uv run pytest tests/e2e/

# Run with coverage
uv run pytest --cov=.
```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes following the architecture patterns
4. Add tests for new functionality
5. Ensure all tests pass: `uv run pytest`
6. Update documentation as needed
7. Submit a pull request

### Code Style

- Follow PEP 8 style guidelines
- Use type hints consistently
- Write comprehensive docstrings
- Include unit tests for new features

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- OpenAI for providing the language models
- LangChain team for the excellent orchestration framework
- PyMuPDF for robust PDF processing capabilities
- Click for the powerful CLI framework
- Pydantic for data validation and modeling

## Changelog

### v2.0.0 (Current)
- Complete architectural refactoring with clean layers
- Dependency injection container implementation
- Modular CLI interface with batch processing
- Enhanced error handling and fallback mechanisms
- Support for multiple AI providers
- Comprehensive testing framework

### v1.0.0 (Legacy)
- Basic PDF parsing and analysis
- Single-file architecture
- Limited configuration options