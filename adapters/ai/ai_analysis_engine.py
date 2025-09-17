"""
AI-powered analysis engine implementation.
"""

import json
import logging
import time
from typing import Dict, Any, Optional, List
from datetime import datetime
import asyncio
import re

from core.analyzer import BaseAnalysisEngine
from domain.models.paper import Paper
from domain.models.analysis import PaperAnalysis, AnalysisStatus, AnalysisMetrics
from adapters.ai import BaseAIAdapter
from core.exceptions import PaperAnalysisError, AIServiceError
from infrastructure.config.settings import Settings


logger = logging.getLogger(__name__)


class AIAnalysisEngine(BaseAnalysisEngine):
    """AI-powered paper analysis engine."""

    def __init__(self, ai_adapter: BaseAIAdapter, config: Dict[str, Any]):
        super().__init__(config)
        self.ai_adapter = ai_adapter
        self.prompt_manager = PromptManager(config)
        self.tools_loader = ToolsLoader(config)

    async def analyze_paper(self, paper: Paper) -> PaperAnalysis:
        """Analyze a single paper using AI."""
        start_time = time.time()

        try:
            # Create analysis object
            analysis = PaperAnalysis(
                id="",
                paper_id=paper.id,
                title="",
                summary="",
                problem="",
                solution="",
                limitations="",
                key_contributions="",
                status=AnalysisStatus.IN_PROGRESS,
                model_used=self.ai_adapter.model,
                prompt_version=self.config.get('prompt_version', 'EN_2_0')
            )

            # Truncate content if too long
            max_length = self.config.get('max_paper_length', 128000)
            content = paper.content
            if len(content) > max_length:
                content = content[:max_length] + "\n\n[Note: Paper truncated due to length limitations]"

            # Get prompt and tools
            prompt = self.prompt_manager.get_analysis_prompt(content)
            tools = self.tools_loader.get_tools_for_analysis(analysis.prompt_version)

            # Generate analysis using AI
            result = await self._generate_analysis(content, prompt, tools)

            # Parse and validate result
            parsed_result = self._parse_analysis_result(result, analysis.prompt_version)

            # Update analysis with results
            analysis.title = parsed_result.get('title', paper.metadata.title or 'Untitled Paper')
            analysis.summary = parsed_result.get('summary', '')
            analysis.problem = parsed_result.get('problem', '')
            analysis.solution = parsed_result.get('solution', '')
            analysis.limitations = parsed_result.get('limitations', '')
            analysis.key_contributions = parsed_result.get('key_contributions', '')
            analysis.research_significance = parsed_result.get('research_significance')
            analysis.raw_response = result
            analysis.status = AnalysisStatus.COMPLETED

            # Calculate metrics
            analysis.metrics.processing_time = time.time() - start_time
            analysis.metrics.token_count = self.ai_adapter.estimate_tokens(content + result)

            # Set confidence score based on result quality
            analysis.metrics.confidence_score = self._calculate_confidence_score(parsed_result)

            logger.info(f"Successfully analyzed paper {paper.id} in {analysis.metrics.processing_time:.2f}s")
            return analysis

        except Exception as e:
            logger.error(f"Failed to analyze paper {paper.id}: {e}")
            return PaperAnalysis(
                id="",
                paper_id=paper.id,
                title="Analysis Failed",
                summary="",
                problem="",
                solution="",
                limitations="",
                key_contributions="",
                status=AnalysisStatus.FAILED,
                error_message=str(e),
                metrics=AnalysisMetrics(processing_time=time.time() - start_time)
            )

    async def _generate_analysis(self, content: str, prompt: str, tools: Optional[Dict[str, Any]]) -> str:
        """Generate analysis using AI adapter."""
        try:
            # Try function calling first if enabled
            if self.config.get('enable_function_calling', True) and tools:
                try:
                    result = await self.ai_adapter.generate_structured_response(prompt, tools['functions'][0]['parameters'])
                    return json.dumps(result)
                except Exception as e:
                    logger.warning(f"Function calling failed, falling back to regular generation: {e}")

            # Fallback to regular text generation
            result = await self.ai_adapter.generate_response(prompt)

            # Try to extract JSON from result
            try:
                parsed = self._extract_json_from_text(result)
                return json.dumps(parsed)
            except Exception:
                # Return raw text if JSON extraction fails
                return result

        except Exception as e:
            raise AIServiceError(f"Failed to generate analysis: {e}")

    def _parse_analysis_result(self, result: str, prompt_version: str) -> Dict[str, Any]:
        """Parse analysis result from AI response."""
        try:
            # Try to parse as JSON first
            parsed = json.loads(result)
            return self._normalize_analysis_result(parsed, prompt_version)
        except json.JSONDecodeError:
            # Extract JSON from text if possible
            try:
                json_data = self._extract_json_from_text(result)
                return self._normalize_analysis_result(json_data, prompt_version)
            except Exception:
                # Create basic result from text
                return self._create_basic_result_from_text(result)

    def _extract_json_from_text(self, text: str) -> Dict[str, Any]:
        """Extract JSON object from text."""
        # Look for JSON pattern
        json_match = re.search(r'\{[\s\S]*\}', text)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass

        raise ValueError("No valid JSON found in text")

    def _normalize_analysis_result(self, result: Dict[str, Any], prompt_version: str) -> Dict[str, Any]:
        """Normalize analysis result to expected format."""
        # Field mapping for different possible field names
        field_mapping = {
            "title": ["title"],
            "summary": ["summary", "paper_overview", "overview"],
            "problem": ["problem", "research_problem", "challenge"],
            "solution": ["solution", "methodology", "method", "approach"],
            "limitations": ["limitations", "limitations_analysis", "weaknesses"],
            "key_contributions": ["key_contributions", "contributions", "academic_contributions"],
            "research_significance": ["research_significance", "significance", "impact"]
        }

        normalized = {}

        # Determine expected fields based on version
        expected_fields = ["title", "summary", "problem", "solution", "limitations", "key_contributions"]
        if prompt_version.endswith("_2_0"):
            expected_fields.append("research_significance")

        for field in expected_fields:
            value = None
            # Try to find value from mapped field names
            for possible_field in field_mapping.get(field, [field]):
                if possible_field in result and result[possible_field]:
                    value = str(result[possible_field])
                    break

            # If still no value, try to create one
            if not value:
                value = self._generate_field_value(field, result)

            normalized[field] = value or ""

        return normalized

    def _generate_field_value(self, field: str, result: Dict[str, Any]) -> Optional[str]:
        """Generate a value for a missing field based on available information."""
        # This is a simple implementation - can be enhanced with AI-based inference
        field_strategies = {
            "title": lambda r: r.get("summary", "")[:100] + "..." if r.get("summary") else None,
            "summary": lambda r: f"This paper addresses {r.get('problem', 'a research challenge')} using {r.get('solution', 'a novel approach')}.",
            "problem": lambda r: "Research problem not explicitly stated.",
            "solution": lambda r: "Solution approach not explicitly described.",
            "limitations": lambda r: "Limitations not explicitly discussed.",
            "key_contributions": lambda r: "Contributions not explicitly summarized.",
            "research_significance": lambda r: "Research significance not explicitly stated."
        }

        strategy = field_strategies.get(field)
        if strategy:
            return strategy(result)
        return None

    def _create_basic_result_from_text(self, text: str) -> Dict[str, Any]:
        """Create basic result from raw text when parsing fails."""
        # Simple text analysis to extract basic information
        lines = text.split('\n')
        first_line = lines[0].strip() if lines else ""

        return {
            "title": first_line[:100] if first_line else "Untitled",
            "summary": text[:500] + "..." if len(text) > 500 else text,
            "problem": "Unable to extract specific problem statement",
            "solution": "Unable to extract specific solution",
            "limitations": "Unable to extract limitations",
            "key_contributions": "Unable to extract contributions",
            "research_significance": None
        }

    def _calculate_confidence_score(self, result: Dict[str, Any]) -> float:
        """Calculate confidence score based on result quality."""
        score = 0.0
        total_weight = 0.0

        # Check field completeness
        fields = ['title', 'summary', 'problem', 'solution', 'limitations', 'key_contributions']
        weights = [0.15, 0.25, 0.15, 0.2, 0.1, 0.15]

        for field, weight in zip(fields, weights):
            if field in result and result[field] and len(str(result[field])) > 20:
                score += weight
            total_weight += weight

        # Add research significance if present
        if 'research_significance' in result and result['research_significance']:
            score += 0.1
            total_weight += 0.1

        return score / total_weight if total_weight > 0 else 0.0


class PromptManager:
    """Manages analysis prompts."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.prompts_dir = config.get('prompts_dir', 'prompts')
        self._load_prompts()

    def _load_prompts(self):
        """Load prompt templates."""
        # For now, we'll use hardcoded prompts
        # In a real implementation, these would be loaded from files
        self.prompts = {
            'EN': self._get_english_prompt(),
            'EN_2_0': self._get_english_enhanced_prompt(),
            'ZH': self._get_chinese_prompt(),
            'ZH_2_0': self._get_chinese_enhanced_prompt()
        }

    def get_analysis_prompt(self, content: str) -> str:
        """Get analysis prompt for content."""
        version = self.config.get('prompt_version', 'EN_2_0')
        prompt_template = self.prompts.get(version, self.prompts['EN_2_0'])
        return prompt_template.format(paper_text=content)

    def _get_english_prompt(self) -> str:
        """Get English prompt template."""
        return """Please analyze the following academic paper:

{paper_text}

You must provide meaningful analysis for ALL required fields:
- title: Paper title or descriptive title based on content
- summary: Comprehensive summary of the paper
- problem: Research problem or challenge addressed
- solution: Proposed solution or methodology
- limitations: Limitations or weaknesses
- key_contributions: Main contributions

Never leave any field empty or use "Not provided". Always provide meaningful analysis.

Return your analysis as a valid JSON object."""

    def _get_english_enhanced_prompt(self) -> str:
        """Get enhanced English prompt template."""
        return """Please conduct a deep analysis of the following academic paper:

{paper_text}

CRITICAL REQUIREMENTS:
- You MUST provide detailed analysis for ALL required fields
- Never leave any field empty or use "Not provided" - this is unacceptable
- When explicit information is not available, make reasonable inferences based on the paper content
- Be proactive in identifying implicit contributions and limitations
- Focus on specific technical details rather than generic statements

Required fields:
- title: Paper title (create descriptive title if not provided)
- summary: Comprehensive summary synthesizing from all sections
- problem: Specific research problem or challenge
- solution: Detailed methodology or approach
- limitations: Technical limitations and potential improvements
- key_contributions: Main innovations and contributions
- research_significance: Impact and significance of the work

Return your analysis as a valid JSON object with all required fields."""

    def _get_chinese_prompt(self) -> str:
        """Get Chinese prompt template."""
        return """请分析以下学术论文：

{paper_text}

您必须为所有必需字段提供有意义的分析：
- title: 论文标题
- summary: 论文内容总结
- problem: 研究问题
- solution: 解决方案
- limitations: 局限性
- key_contributions: 主要贡献

严禁留空任何字段或使用"Not provided"。请使用analyze_paper函数提供您的完整分析。"""

    def _get_chinese_enhanced_prompt(self) -> str:
        """Get enhanced Chinese prompt template."""
        return """请对以下学术论文进行深度分析：

{paper_text}

关键分析要求：
- 您必须为所有必需字段提供详细分析
- 严禁留空任何字段或使用"Not provided" - 这是不可接受的
- 当论文中没有直接明确的信息时，请基于内容进行合理推断
- 主动识别隐含的贡献和局限性
- 提供具体的技术细节，避免泛泛而谈

必需字段：
- title: 论文标题（如未提供请创建描述性标题）
- summary: 全面总结论文内容
- problem: 具体研究问题或挑战
- solution: 详细方法论或方法
- limitations: 技术局限性和潜在改进
- key_contributions: 主要创新和贡献
- research_significance: 工作的影响和意义

请使用analyze_paper函数提供您的全面分析，确保所有字段都完成了有意义的内容。"""


class ToolsLoader:
    """Loads tools configuration for function calling."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.tools_config = self._load_tools_config()

    def _load_tools_config(self) -> Dict[str, Any]:
        """Load tools configuration."""
        # For now, return hardcoded configuration
        # In a real implementation, this would be loaded from a JSON file
        return {
            "versions": {
                "1.0": {
                    "functions": [{
                        "name": "analyze_paper",
                        "description": "Analyze and extract key information from an academic paper",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "title": {"type": "string", "description": "Paper title"},
                                "summary": {"type": "string", "description": "Brief summary of the paper's content"},
                                "problem": {"type": "string", "description": "What problem the paper addresses"},
                                "solution": {"type": "string", "description": "How the paper solves the problem"},
                                "limitations": {"type": "string", "description": "Limitations or unresolved issues"},
                                "key_contributions": {"type": "string", "description": "Main contributions of the paper"}
                            },
                            "required": ["title", "summary", "problem", "solution", "limitations", "key_contributions"]
                        }
                    }]
                },
                "2.0": {
                    "functions": [{
                        "name": "analyze_paper",
                        "description": "Analyze and extract key information from an academic paper with enhanced analysis",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "title": {"type": "string", "description": "Paper title"},
                                "summary": {"type": "string", "description": "Brief summary of the paper's content"},
                                "problem": {"type": "string", "description": "What problem the paper addresses"},
                                "solution": {"type": "string", "description": "How the paper solves the problem"},
                                "limitations": {"type": "string", "description": "Limitations or unresolved issues"},
                                "key_contributions": {"type": "string", "description": "Main contributions of the paper"},
                                "research_significance": {"type": "string", "description": "Research significance and impact"}
                            },
                            "required": ["title", "summary", "problem", "solution", "limitations", "key_contributions", "research_significance"]
                        }
                    }]
                }
            }
        }

    def get_tools_for_analysis(self, prompt_version: str) -> Optional[Dict[str, Any]]:
        """Get tools configuration for the specified prompt version."""
        version = "2.0" if prompt_version.endswith("_2_0") else "1.0"
        return self.tools_config["versions"].get(version)