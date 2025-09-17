"""
DeepSeek service adapter.
"""

import json
import logging
from typing import Optional, Dict, Any, List
from openai import AsyncOpenAI

from .base import BaseAIAdapter, AIResponse
from core.exceptions import AIServiceError


logger = logging.getLogger(__name__)


class DeepSeekAdapter(BaseAIAdapter):
    """DeepSeek API adapter."""

    def __init__(self, api_key: str, model: str = "deepseek-chat", base_url: Optional[str] = None):
        super().__init__(api_key, model, base_url or "https://api.deepseek.com/v1")
        self.client = AsyncOpenAI(api_key=api_key, base_url=self.base_url)
        self.supports_function_calling = True  # DeepSeek supports function calling

    async def generate_response(self, prompt: str, tools: Optional[Dict[str, Any]] = None) -> str:
        """Generate response from DeepSeek."""
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
            logger.error(f"DeepSeek API error: {e}")
            raise AIServiceError(f"DeepSeek API error: {e}")

    async def generate_structured_response(self, prompt: str, schema: Dict[str, Any]) -> Dict[str, Any]:
        """Generate structured response from DeepSeek."""
        # Create tools configuration from schema
        tools = {
            "functions": [{
                "name": "analyze_paper",
                "description": "Analyze academic paper and extract key information",
                "parameters": schema
            }],
            "function_call": {"name": "analyze_paper"}
        }

        try:
            response = await self.generate_response(prompt, tools)
            function_data = self._extract_function_call(response)
            if function_data:
                return function_data
        except Exception as e:
            logger.warning(f"Function calling failed, falling back to JSON parsing: {e}")

        # Fallback: try direct JSON generation
        json_prompt = f"{prompt}\n\nPlease provide your analysis as a valid JSON object with the following schema:\n{json.dumps(schema, indent=2)}"

        try:
            response = await self.generate_response(json_prompt)
            return self._extract_json_from_response(response)
        except Exception as e:
            raise AIServiceError(f"Failed to generate structured response: {e}")

    def _extract_content(self, response) -> str:
        """Extract content from DeepSeek response."""
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

    def _extract_json_from_response(self, response: str) -> Dict[str, Any]:
        """Extract JSON from text response."""
        try:
            # Try direct JSON parsing first
            return json.loads(response)
        except json.JSONDecodeError:
            # Try to find JSON in the text
            import re
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                try:
                    return json.loads(json_match.group())
                except json.JSONDecodeError:
                    pass

        raise AIServiceError("No valid JSON found in response")

    def get_model_info(self) -> Dict[str, Any]:
        """Get DeepSeek model information."""
        return {
            'provider': 'deepseek',
            'model': self.model,
            'supports_function_calling': self.supports_function_calling,
            'base_url': self.base_url,
            'max_tokens': 4000,
            'features': ['function_calling', 'json_mode']
        }

    async def test_connection(self) -> bool:
        """Test connection to DeepSeek API."""
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=5
            )
            return True
        except Exception as e:
            logger.error(f"DeepSeek connection test failed: {e}")
            return False

    def get_available_models(self) -> List[str]:
        """Get list of available models."""
        return [
            "deepseek-chat",
            "deepseek-coder"
        ]