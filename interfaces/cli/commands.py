"""
CLI commands implementation.
"""

import asyncio
import json
import logging
import time
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime

from domain.models.paper import Paper
from domain.models.analysis import PaperAnalysis, AnalysisStatus
from core.analyzer import AnalysisOrchestrator
from adapters.parsers import ParserRegistry
from infrastructure.config.settings import Settings
from core.exceptions import PaperAnalysisError


logger = logging.getLogger(__name__)


class AnalysisCommands:
    """CLI command implementations for paper analysis."""

    def __init__(self, container):
        """Initialize commands with dependency injection container."""
        self.container = container
        self.orchestrator = container.get_container().create_orchestrator()
        self.parser_registry = container.get('parser_registry')
        self.config = container.get_container().config

    async def analyze_paper(
        self,
        input_path: str,
        output_path: Optional[str] = None,
        prompt_version: Optional[str] = None,
        model: Optional[str] = None,
        max_length: Optional[int] = None,
        extract_images: bool = False
    ) -> PaperAnalysis:
        """Analyze a single paper."""
        try:
            # Update config with runtime options
            if model:
                self.config.ai.model = model
            if prompt_version:
                self.config.analysis.prompt_version = prompt_version
            if max_length:
                self.config.analysis.max_paper_length = max_length

            # Parse input file
            paper = await self._parse_paper(input_path, extract_images)

            # Analyze paper
            analysis = await self.orchestrator.analyze_paper(paper)

            # Save results if output path specified
            if output_path:
                await self._save_analysis(analysis, output_path)

            return analysis

        except Exception as e:
            logger.error(f"Error analyzing paper {input_path}: {e}")
            raise PaperAnalysisError(f"Failed to analyze paper: {e}")

    async def batch_analyze_papers(
        self,
        input_dir: str,
        output_dir: Optional[str] = None,
        prompt_version: Optional[str] = None,
        model: Optional[str] = None,
        max_length: Optional[int] = None,
        concurrent: int = 3
    ) -> List[PaperAnalysis]:
        """Analyze multiple papers in a directory."""
        try:
            # Update config with runtime options
            if model:
                self.config.ai.model = model
            if prompt_version:
                self.config.analysis.prompt_version = prompt_version
            if max_length:
                self.config.analysis.max_paper_length = max_length

            # Find all paper files
            paper_files = await self._find_paper_files(input_dir)

            if not paper_files:
                raise PaperAnalysisError(f"No paper files found in {input_dir}")

            # Create output directory if specified
            if output_dir:
                Path(output_dir).mkdir(parents=True, exist_ok=True)

            # Process papers concurrently
            semaphore = asyncio.Semaphore(concurrent)
            tasks = []

            for file_path in paper_files:
                task = self._analyze_single_paper_with_semaphore(
                    semaphore, file_path, output_dir, extract_images=False
                )
                tasks.append(task)

            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Process results and handle exceptions
            analyses = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    # Create failed analysis for error tracking
                    failed_analysis = PaperAnalysis(
                        id=f"failed_{i}",
                        paper_id=paper_files[i],
                        title=f"Failed: {Path(paper_files[i]).name}",
                        summary="",
                        problem="",
                        solution="",
                        limitations="",
                        key_contributions="",
                        status=AnalysisStatus.FAILED,
                        error_message=str(result)
                    )
                    analyses.append(failed_analysis)
                    logger.error(f"Failed to analyze {paper_files[i]}: {result}")
                else:
                    analyses.append(result)

            return analyses

        except Exception as e:
            logger.error(f"Error in batch analysis: {e}")
            raise PaperAnalysisError(f"Batch analysis failed: {e}")

    async def test_connection(self) -> bool:
        """Test connection to AI service."""
        try:
            # Create a simple test paper
            test_paper = Paper(
                id="test_connection",
                file_path="test.txt",
                content="This is a test paper for connection verification.",
                paper_type="text"
            )

            # Try to analyze with minimal content
            analysis = await self.orchestrator.analyze_paper(test_paper)

            return analysis.status == AnalysisStatus.COMPLETED

        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False

    def get_system_info(self) -> Dict[str, Any]:
        """Get system information."""
        try:
            return {
                "version": "1.0.0",
                "ai_provider": self.config.ai.provider,
                "ai_model": self.config.ai.model,
                "prompt_version": self.config.analysis.prompt_version,
                "max_paper_length": self.config.analysis.max_paper_length,
                "supported_formats": [".pdf", ".txt", ".md", ".markdown"],
                "container_services": self.container.get_container().get_service_info()
            }
        except Exception as e:
            logger.error(f"Error getting system info: {e}")
            return {"error": str(e)}

    async def _parse_paper(self, file_path: str, extract_images: bool) -> Paper:
        """Parse paper file using appropriate parser."""
        try:
            return await self.parser_registry.parse_file(file_path, extract_images=extract_images)

        except Exception as e:
            logger.error(f"Error parsing paper {file_path}: {e}")
            raise PaperAnalysisError(f"Failed to parse paper: {e}")

    async def _save_analysis(self, analysis: PaperAnalysis, output_path: str):
        """Save analysis results to file."""
        try:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)

            # Convert analysis to dictionary
            analysis_dict = {
                "id": analysis.id,
                "paper_id": analysis.paper_id,
                "title": analysis.title,
                "summary": analysis.summary,
                "problem": analysis.problem,
                "solution": analysis.solution,
                "limitations": analysis.limitations,
                "key_contributions": analysis.key_contributions,
                "research_significance": analysis.research_significance,
                "status": analysis.status.value,
                "model_used": analysis.model_used,
                "prompt_version": analysis.prompt_version,
                "created_at": analysis.created_at.isoformat() if analysis.created_at else None,
                "updated_at": analysis.updated_at.isoformat() if analysis.updated_at else None,
                "error_message": analysis.error_message,
                "metrics": {
                    "processing_time": analysis.metrics.processing_time,
                    "token_count": analysis.metrics.token_count,
                    "confidence_score": analysis.metrics.confidence_score,
                    "quality_score": analysis.get_quality_score()
                }
            }

            # Save as JSON
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(analysis_dict, f, indent=2, ensure_ascii=False)

            logger.info(f"Analysis saved to {output_path}")

        except Exception as e:
            logger.error(f"Error saving analysis to {output_path}: {e}")
            raise PaperAnalysisError(f"Failed to save analysis: {e}")

    async def _find_paper_files(self, input_dir: str) -> List[str]:
        """Find all paper files in directory."""
        supported_extensions = {'.pdf', '.txt', '.md', '.markdown'}
        paper_files = []

        input_path = Path(input_dir)
        if not input_path.exists():
            raise PaperAnalysisError(f"Input directory does not exist: {input_dir}")

        for file_path in input_path.rglob('*'):
            if file_path.is_file() and file_path.suffix.lower() in supported_extensions:
                paper_files.append(str(file_path))

        return sorted(paper_files)

    async def _analyze_single_paper_with_semaphore(
        self, semaphore: asyncio.Semaphore, file_path: str, output_dir: Optional[str], extract_images: bool
    ) -> PaperAnalysis:
        """Analyze single paper with semaphore control."""
        async with semaphore:
            try:
                # Determine output path
                output_path = None
                if output_dir:
                    input_file = Path(file_path)
                    output_file = Path(output_dir) / f"{input_file.stem}_analysis.json"
                    output_path = str(output_file)

                # Parse and analyze
                paper = await self._parse_paper(file_path, extract_images)
                analysis = await self.orchestrator.analyze_paper(paper)

                # Save results
                if output_path:
                    await self._save_analysis(analysis, output_path)

                return analysis

            except Exception as e:
                logger.error(f"Error processing {file_path}: {e}")
                raise