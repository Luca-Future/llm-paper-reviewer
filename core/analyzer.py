"""
Core analysis engine interfaces and implementations.
"""

from abc import ABC, abstractmethod
from typing import Protocol, List, Optional, Dict, Any
from datetime import datetime
import asyncio

from domain.models.paper import Paper
from domain.models.analysis import PaperAnalysis, AnalysisStatus
from core.exceptions import PaperAnalysisError, AIServiceError


class AnalysisEngine(Protocol):
    """Protocol for paper analysis engines."""

    async def analyze_paper(self, paper: Paper) -> PaperAnalysis:
        """Analyze a single paper."""
        ...

    async def batch_analyze(self, papers: List[Paper]) -> List[PaperAnalysis]:
        """Analyze multiple papers."""
        ...

    def get_engine_info(self) -> Dict[str, Any]:
        """Get engine information."""
        ...


class BaseAnalysisEngine(ABC):
    """Base class for analysis engines."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.engine_name = self.__class__.__name__

    @abstractmethod
    async def analyze_paper(self, paper: Paper) -> PaperAnalysis:
        """Analyze a single paper."""
        pass

    async def batch_analyze(self, papers: List[Paper]) -> List[PaperAnalysis]:
        """Analyze multiple papers concurrently."""
        tasks = [self.analyze_paper(paper) for paper in papers]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results and handle exceptions
        processed_results = []
        for paper, result in zip(papers, results):
            if isinstance(result, Exception):
                # Create failed analysis result
                analysis = PaperAnalysis(
                    id="",
                    paper_id=paper.id,
                    title="Analysis Failed",
                    summary="",
                    problem="",
                    solution="",
                    limitations="",
                    key_contributions="",
                    status=AnalysisStatus.FAILED,
                    error_message=str(result)
                )
            else:
                processed_results.append(result)

        return processed_results

    def get_engine_info(self) -> Dict[str, Any]:
        """Get engine information."""
        return {
            'name': self.engine_name,
            'type': 'base',
            'config': self.config,
            'version': '1.0.0'
        }


class AnalysisOrchestrator:
    """Orchestrates multiple analysis engines."""

    def __init__(self, primary_engine: AnalysisEngine, fallback_engine: Optional[AnalysisEngine] = None):
        self.primary_engine = primary_engine
        self.fallback_engine = fallback_engine

    async def analyze_paper(self, paper: Paper) -> PaperAnalysis:
        """Analyze paper with fallback support."""
        try:
            return await self.primary_engine.analyze_paper(paper)
        except Exception as primary_error:
            if self.fallback_engine:
                try:
                    # Try fallback engine
                    fallback_result = await self.fallback_engine.analyze_paper(paper)
                    # Add note about fallback usage
                    fallback_result.raw_response = (
                        f"FALLBACK ANALYSIS (Primary failed: {str(primary_error)})\n\n"
                        f"{fallback_result.raw_response or ''}"
                    )
                    return fallback_result
                except Exception as fallback_error:
                    # Create failed analysis result
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
                        error_message=f"Primary: {str(primary_error)}, Fallback: {str(fallback_error)}"
                    )
            else:
                # No fallback available
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
                    error_message=str(primary_error)
                )

    async def batch_analyze(self, papers: List[Paper]) -> List[PaperAnalysis]:
        """Analyze multiple papers with fallback support."""
        tasks = [self.analyze_paper(paper) for paper in papers]
        return await asyncio.gather(*tasks)

    def get_orchestrator_info(self) -> Dict[str, Any]:
        """Get orchestrator information."""
        info = {
            'primary_engine': self.primary_engine.get_engine_info(),
            'has_fallback': self.fallback_engine is not None
        }
        if self.fallback_engine:
            info['fallback_engine'] = self.fallback_engine.get_engine_info()
        return info


class AnalysisValidator:
    """Validates analysis results."""

    @staticmethod
    def validate_analysis(analysis: PaperAnalysis) -> List[str]:
        """Validate analysis result and return list of issues."""
        issues = []

        # Check required fields
        required_fields = ['title', 'summary', 'problem', 'solution', 'limitations', 'key_contributions']
        for field in required_fields:
            value = getattr(analysis, field)
            if not value or len(str(value).strip()) < 10:
                issues.append(f"Field '{field}' is too short or empty")

        # Check content quality
        if analysis.metrics.completeness_score < 0.5:
            issues.append("Low completeness score")

        if analysis.metrics.coherence_score < 0.3:
            issues.append("Low coherence score")

        # Check for placeholder text
        placeholder_patterns = ['not provided', 'n/a', 'none', 'null']
        all_content = f"{analysis.title} {analysis.summary} {analysis.problem} {analysis.solution}"
        for pattern in placeholder_patterns:
            if pattern in all_content.lower():
                issues.append(f"Found placeholder text: '{pattern}'")

        return issues

    @staticmethod
    def validate_paper(paper: Paper) -> List[str]:
        """Validate paper input."""
        issues = []

        if not paper.content or len(paper.content.strip()) < 50:
            issues.append("Paper content is too short or empty")

        if paper.get_word_count() < 100:
            issues.append("Paper has insufficient word count")

        # Check for content quality
        if len(paper.content.split('\n')) < 5:
            issues.append("Paper has insufficient structure")

        return issues