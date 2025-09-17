"""
OpenAI service adapter.
"""

import json
import logging
from typing import Optional, Dict, Any, List
from openai import AsyncOpenAI

from .base import BaseAIAdapter, AIResponse
from core.exceptions import AIServiceError


logger = logging.getLogger(__name__)


class OpenAIAdapter(BaseAIAdapter):
    """OpenAI API adapter."""

    def __init__(self, api_key: str, model: str = "gpt-4o", base_url: Optional[str] = None):
        super().__init__(api_key, model, base_url)
        self.client = AsyncOpenAI(api_key=api_key, base_url=base_url)
        self.supports_function_calling = True

    async def generate_response(self, prompt: str, tools: Optional[Dict[str, Any]] = None) -> str:
        """Generate response from OpenAI."""
        if not self.validate_api_key():
            raise AIServiceError("Invalid API key")

        kwargs = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.1,
            "max_tokens": 4000
        }

        # Add function calling if supported and tools provided
        if tools and self.supports_function_calling:
            kwargs["functions"] = tools.get("functions", [])
            kwargs["function_call"] = tools.get("function_call", {"name": "analyze_paper"})

        try:
            response = await self.with_retry(self.client.chat.completions.create, **kwargs)
            return self._extract_content(response)
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise AIServiceError(f"OpenAI API error: {e}")

    async def generate_structured_response(self, prompt: str, schema: Dict[str, Any]) -> Dict[str, Any]:
        """Generate structured response from OpenAI."""
        # Create tools configuration from schema
        tools = {
            "functions": [{
                "name": "analyze_paper",
                "description": "Analyze academic paper and extract key information",
                "parameters": schema
            }],
            "function_call": {"name": "analyze_paper"}
        }

        response = await self.generate_response(prompt, tools)

        # Try to parse as function call first
        try:
            function_data = self._extract_function_call(response)
            if function_data:
                return function_data
        except (json.JSONDecodeError, KeyError):
            pass

        # Fallback: try to parse as JSON
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            raise AIServiceError("Unable to parse structured response")

    def _extract_content(self, response) -> str:
        """Extract content from OpenAI response."""
        choice = response.choices[0]
        message = choice.message

        # Check if it's a function call
        if hasattr(message, 'function_call') and message.function_call:
            # For function calls, return the function call data as JSON
            function_data = {
                'name': message.function_call.name,
                'arguments': message.function_call.arguments
            }
            return json.dumps(function_data)

        # Regular content
        return message.content or ""

    def _extract_function_call(self, response: str) -> Optional[Dict[str, Any]]:
        """Extract function call data from response."""
        try:
            data = json.loads(response)
            if isinstance(data, dict) and 'name' in data and 'arguments' in data:
                return json.loads(data['arguments'])
        except (json.JSONDecodeError, KeyError):
            pass
        return None

    def get_model_info(self) -> Dict[str, Any]:
        """Get OpenAI model information."""
        return {
            'provider': 'openai',
            'model': self.model,
            'supports_function_calling': self.supports_function_calling,
            'base_url': self.base_url,
            'max_tokens': 4000,
            'features': ['function_calling', 'json_mode']
        }

    async def test_connection(self) -> bool:
        """Test connection to OpenAI API."""
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=5
            )
            return True
        except Exception as e:
            logger.error(f"OpenAI connection test failed: {e}")
            return False

    def get_available_models(self) -> List[str]:
        """Get list of available models."""
        return [
            "gpt-4o",
            "gpt-4o-mini",
            "gpt-4-turbo",
            "gpt-4",
            "gpt-3.5-turbo"
        ]