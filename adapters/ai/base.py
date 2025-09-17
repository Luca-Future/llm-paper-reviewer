"""
Base classes for AI service adapters.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
import asyncio
import time


class BaseAIAdapter(ABC):
    """Base class for AI service adapters."""

    def __init__(self, api_key: str, model: str, base_url: Optional[str] = None):
        self.api_key = api_key
        self.model = model
        self.base_url = base_url
        self.timeout = 30
        self.max_retries = 3

    @abstractmethod
    async def generate_response(self, prompt: str, tools: Optional[Dict[str, Any]] = None) -> str:
        """Generate response from AI service."""
        pass

    @abstractmethod
    async def generate_structured_response(self, prompt: str, schema: Dict[str, Any]) -> Dict[str, Any]:
        """Generate structured response from AI service."""
        pass

    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]:
        """Get model information."""
        pass

    async def with_retry(self, func, *args, **kwargs):
        """Execute function with retry logic."""
        last_error = None
        for attempt in range(self.max_retries):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                last_error = e
                if attempt < self.max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff
                    await asyncio.sleep(wait_time)
                else:
                    raise

        raise last_error

    def validate_api_key(self) -> bool:
        """Validate API key format."""
        if not self.api_key:
            return False

        # Basic validation - check if it looks like a valid key
        if len(self.api_key) < 10:
            return False

        return True

    def estimate_tokens(self, text: str) -> int:
        """Estimate token count for text."""
        # Simple estimation: ~4 characters per token
        return max(1, len(text) // 4)


class AIResponse:
    """Standardized AI response wrapper."""

    def __init__(self, content: str, metadata: Optional[Dict[str, Any]] = None):
        self.content = content
        self.metadata = metadata or {}
        self.timestamp = time.time()

    def get_function_calls(self) -> List[Dict[str, Any]]:
        """Extract function calls from response."""
        return self.metadata.get('function_calls', [])

    def is_function_call(self) -> bool:
        """Check if response is a function call."""
        return len(self.get_function_calls()) > 0

    def get_token_usage(self) -> Dict[str, int]:
        """Get token usage information."""
        return self.metadata.get('token_usage', {'prompt_tokens': 0, 'completion_tokens': 0, 'total_tokens': 0})

    def to_dict(self) -> Dict[str, Any]:
        """Convert response to dictionary."""
        return {
            'content': self.content,
            'metadata': self.metadata,
            'timestamp': self.timestamp,
            'is_function_call': self.is_function_call(),
            'token_usage': self.get_token_usage()
        }