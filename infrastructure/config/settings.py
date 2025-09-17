"""
Configuration management settings.
"""

import os
import yaml
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from pathlib import Path


@dataclass
class AISettings:
    """AI service configuration."""
    provider: str = "openai"
    model: str = "gpt-4o"
    api_key: str = ""
    base_url: Optional[str] = None
    temperature: float = 0.1
    max_tokens: int = 4000
    timeout: int = 30
    max_retries: int = 3


@dataclass
class AnalysisSettings:
    """Analysis configuration."""
    max_paper_length: int = 128000
    prompt_version: str = "EN_2_0"
    enable_function_calling: bool = True
    confidence_threshold: float = 0.7
    field_mapping: Dict[str, List[str]] = field(default_factory=lambda: {
        "title": ["title"],
        "summary": ["summary", "paper_overview"],
        "problem": ["problem", "research_problem"],
        "solution": ["solution", "methodology"],
        "limitations": ["limitations", "limitations_analysis"],
        "key_contributions": ["key_contributions", "academic_contributions"],
        "research_significance": ["research_significance"]
    })


@dataclass
class LoggingSettings:
    """Logging configuration."""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_path: Optional[str] = None
    max_file_size: str = "10MB"
    backup_count: int = 5


@dataclass
class StorageSettings:
    """Storage configuration."""
    output_dir: str = "output"
    temp_dir: str = "temp"
    image_dir: str = "images"
    enable_caching: bool = True
    cache_ttl: int = 3600


@dataclass
class Settings:
    """Main application settings."""
    ai: AISettings = field(default_factory=AISettings)
    analysis: AnalysisSettings = field(default_factory=AnalysisSettings)
    logging: LoggingSettings = field(default_factory=LoggingSettings)
    storage: StorageSettings = field(default_factory=StorageSettings)

    @classmethod
    def from_yaml(cls, config_path: str) -> 'Settings':
        """Load settings from YAML file."""
        config_path = Path(config_path)
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")

        with open(config_path, 'r', encoding='utf-8') as f:
            config_data = yaml.safe_load(f)

        # Create nested dataclass instances
        ai_settings = AISettings(**config_data.get('ai', {}))
        analysis_settings = AnalysisSettings(**config_data.get('analysis', {}))
        logging_settings = LoggingSettings(**config_data.get('logging', {}))
        storage_settings = StorageSettings(**config_data.get('storage', {}))

        return cls(
            ai=ai_settings,
            analysis=analysis_settings,
            logging=logging_settings,
            storage=storage_settings
        )

    @classmethod
    def from_env(cls) -> 'Settings':
        """Load settings from environment variables."""
        # AI settings from environment
        ai_settings = AISettings(
            provider=os.getenv('AI_PROVIDER', 'openai'),
            model=os.getenv('AI_MODEL', 'gpt-4o'),
            api_key=os.getenv('OPENAI_API_KEY', ''),
            base_url=os.getenv('OPENAI_BASE_URL'),
            temperature=float(os.getenv('AI_TEMPERATURE', '0.1')),
            max_tokens=int(os.getenv('AI_MAX_TOKENS', '4000')),
            timeout=int(os.getenv('AI_TIMEOUT', '30')),
            max_retries=int(os.getenv('AI_MAX_RETRIES', '3'))
        )

        # Analysis settings from environment
        analysis_settings = AnalysisSettings(
            max_paper_length=int(os.getenv('MAX_PAPER_LENGTH', '128000')),
            prompt_version=os.getenv('PROMPT_VERSION', 'EN_2_0'),
            enable_function_calling=os.getenv('ENABLE_FUNCTION_CALLING', 'true').lower() == 'true',
            confidence_threshold=float(os.getenv('CONFIDENCE_THRESHOLD', '0.7'))
        )

        # Logging settings from environment
        logging_settings = LoggingSettings(
            level=os.getenv('LOG_LEVEL', 'INFO'),
            format=os.getenv('LOG_FORMAT', '%(asctime)s - %(name)s - %(levelname)s - %(message)s'),
            file_path=os.getenv('LOG_FILE_PATH'),
            max_file_size=os.getenv('LOG_MAX_FILE_SIZE', '10MB'),
            backup_count=int(os.getenv('LOG_BACKUP_COUNT', '5'))
        )

        # Storage settings from environment
        storage_settings = StorageSettings(
            output_dir=os.getenv('OUTPUT_DIR', 'output'),
            temp_dir=os.getenv('TEMP_DIR', 'temp'),
            image_dir=os.getenv('IMAGE_DIR', 'images'),
            enable_caching=os.getenv('ENABLE_CACHING', 'true').lower() == 'true',
            cache_ttl=int(os.getenv('CACHE_TTL', '3600'))
        )

        return cls(
            ai=ai_settings,
            analysis=analysis_settings,
            logging=logging_settings,
            storage=storage_settings
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert settings to dictionary."""
        return {
            'ai': self.ai.__dict__,
            'analysis': self.analysis.__dict__,
            'logging': self.logging.__dict__,
            'storage': self.storage.__dict__
        }