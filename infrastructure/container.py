"""
Simple dependency injection container.
"""

import logging
from typing import Dict, Any, Optional, Type, Callable
from dataclasses import dataclass, field

from infrastructure.config.settings import Settings
from adapters.ai import BaseAIAdapter, OpenAIAdapter, DeepSeekAdapter
from adapters.parsers import BaseParser, PDFParser, TextParser, ParserRegistry
from core.analyzer import BaseAnalysisEngine, AnalysisOrchestrator
from core.exceptions import PaperAnalysisError


logger = logging.getLogger(__name__)


@dataclass
class ServiceDescriptor:
    """Service descriptor for dependency injection."""
    factory: Callable
    singleton: bool = True
    instance: Optional[Any] = field(default=None)
    dependencies: list = field(default_factory=list)


class DIContainer:
    """Simple dependency injection container."""

    def __init__(self, config: Settings):
        self.config = config
        self.services: Dict[str, ServiceDescriptor] = {}
        self._register_services()

    def _register_services(self):
        """Register all services with their factories."""
        # AI adapters
        self.register_factory(
            'ai_adapter',
            self._create_ai_adapter,
            singleton=True
        )

        # Parsers
        self.register_factory(
            'pdf_parser',
            lambda: PDFParser(self.config.to_dict()),
            singleton=True
        )

        self.register_factory(
            'text_parser',
            lambda: TextParser(self.config.to_dict()),
            singleton=True
        )

        self.register_factory(
            'parser_registry',
            self._create_parser_registry,
            singleton=True
        )

        # Analysis engine
        self.register_factory(
            'analysis_engine',
            self._create_analysis_engine,
            singleton=True
        )

        # Additional services can be registered here

    def register_factory(self, name: str, factory: Callable, singleton: bool = True):
        """Register a service factory."""
        self.services[name] = ServiceDescriptor(
            factory=factory,
            singleton=singleton
        )

    def register_instance(self, name: str, instance: Any):
        """Register a service instance."""
        self.services[name] = ServiceDescriptor(
            factory=lambda: instance,
            singleton=True,
            instance=instance
        )

    def get(self, name: str) -> Any:
        """Get a service instance."""
        if name not in self.services:
            raise PaperAnalysisError(f"Service '{name}' not registered")

        descriptor = self.services[name]

        if descriptor.singleton and descriptor.instance is not None:
            return descriptor.instance

        # Create instance
        try:
            # Resolve dependencies
            kwargs = {}
            for dep_name in descriptor.dependencies:
                kwargs[dep_name] = self.get(dep_name)

            instance = descriptor.factory(**kwargs)

            if descriptor.singleton:
                descriptor.instance = instance

            return instance

        except Exception as e:
            logger.error(f"Failed to create service '{name}': {e}")
            raise PaperAnalysisError(f"Failed to create service '{name}': {e}")

    def _create_ai_adapter(self) -> BaseAIAdapter:
        """Create AI adapter based on configuration."""
        ai_config = self.config.ai

        if ai_config.provider.lower() == 'openai':
            return OpenAIAdapter(
                api_key=ai_config.api_key,
                model=ai_config.model,
                base_url=ai_config.base_url
            )
        elif ai_config.provider.lower() == 'deepseek':
            return DeepSeekAdapter(
                api_key=ai_config.api_key,
                model=ai_config.model,
                base_url=ai_config.base_url
            )
        else:
            raise PaperAnalysisError(f"Unsupported AI provider: {ai_config.provider}")

    def _create_parser_registry(self) -> ParserRegistry:
        """Create parser registry."""
        registry = ParserRegistry()
        registry.register_parser(self.get('pdf_parser'))
        registry.register_parser(self.get('text_parser'))
        return registry

    def _create_analysis_engine(self) -> BaseAnalysisEngine:
        """Create analysis engine."""
        # Import here to avoid circular imports
        from adapters.ai.ai_analysis_engine import AIAnalysisEngine

        return AIAnalysisEngine(
            ai_adapter=self.get('ai_adapter'),
            config=self.config.to_dict()
        )

    def create_orchestrator(self, fallback_engine: Optional[BaseAnalysisEngine] = None) -> AnalysisOrchestrator:
        """Create analysis orchestrator."""
        primary_engine = self.get('analysis_engine')
        return AnalysisOrchestrator(primary_engine, fallback_engine)

    def get_service_info(self) -> Dict[str, Any]:
        """Get information about all registered services."""
        info = {}
        for name, descriptor in self.services.items():
            info[name] = {
                'singleton': descriptor.singleton,
                'has_instance': descriptor.instance is not None,
                'dependencies': descriptor.dependencies
            }
        return info


class ApplicationContainer:
    """Application-level container with global state."""

    _instance: Optional['ApplicationContainer'] = None
    _container: Optional[DIContainer] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def initialize(self, config: Settings):
        """Initialize the container with configuration."""
        if self._container is None:
            self._container = DIContainer(config)
            logger.info("Application container initialized")

    def get_container(self) -> DIContainer:
        """Get the DI container."""
        if self._container is None:
            raise PaperAnalysisError("Container not initialized")
        return self._container

    def get(self, service_name: str) -> Any:
        """Get a service by name."""
        return self.get_container().get(service_name)

    @classmethod
    def get_instance(cls) -> 'ApplicationContainer':
        """Get the global container instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance


# Global functions for easy access
def get_container() -> DIContainer:
    """Get the global DI container."""
    return ApplicationContainer.get_instance().get_container()


def get_service(service_name: str) -> Any:
    """Get a service by name."""
    return ApplicationContainer.get_instance().get(service_name)


def initialize_container(config: Settings):
    """Initialize the global container."""
    ApplicationContainer.get_instance().initialize(config)