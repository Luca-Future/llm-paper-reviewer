"""
Analysis domain models.
"""

import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any, List
from enum import Enum


class AnalysisStatus(Enum):
    """Analysis status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class AnalysisMetrics:
    """Analysis metrics and quality indicators."""
    confidence_score: float = 0.0
    completeness_score: float = 0.0
    coherence_score: float = 0.0
    technical_depth_score: float = 0.0
    word_count: int = 0
    processing_time: float = 0.0
    token_count: int = 0

    def calculate_overall_score(self) -> float:
        """Calculate overall analysis quality score."""
        weights = {
            'confidence': 0.3,
            'completeness': 0.25,
            'coherence': 0.25,
            'technical_depth': 0.2
        }
        return (
            self.confidence_score * weights['confidence'] +
            self.completeness_score * weights['completeness'] +
            self.coherence_score * weights['coherence'] +
            self.technical_depth_score * weights['technical_depth']
        )


@dataclass
class PaperAnalysis:
    """Paper analysis result domain model."""
    id: str
    paper_id: str
    title: str
    summary: str
    problem: str
    solution: str
    limitations: str
    key_contributions: str
    research_significance: Optional[str] = None
    status: AnalysisStatus = AnalysisStatus.PENDING
    analysis_date: Optional[datetime] = None
    metrics: AnalysisMetrics = field(default_factory=AnalysisMetrics)
    raw_response: Optional[str] = None
    error_message: Optional[str] = None
    prompt_version: str = "EN_2_0"
    model_used: str = ""

    def __post_init__(self):
        """Initialize analysis after creation."""
        if self.analysis_date is None:
            self.analysis_date = datetime.now()

        if not self.id:
            self.id = self._generate_id()

        # Calculate metrics
        self._calculate_metrics()

    def _generate_id(self) -> str:
        """Generate unique ID for the analysis."""
        import hashlib
        content = f"{self.paper_id}_{self.analysis_date.isoformat()}"
        hash_obj = hashlib.md5(content.encode())
        return f"analysis_{hash_obj.hexdigest()[:16]}"

    def _calculate_metrics(self):
        """Calculate analysis metrics."""
        self.metrics.word_count = self.get_total_word_count()

        # Calculate completeness score based on filled fields
        fields = [self.title, self.summary, self.problem, self.solution,
                 self.limitations, self.key_contributions]
        if self.research_significance:
            fields.append(self.research_significance)

        filled_fields = sum(1 for field in fields if field and len(field.strip()) > 10)
        self.metrics.completeness_score = filled_fields / len(fields)

        # Calculate coherence score (simple heuristic)
        self.metrics.coherence_score = self._calculate_coherence_score()

        # Estimate technical depth
        self.metrics.technical_depth_score = self._estimate_technical_depth()

    def _calculate_coherence_score(self) -> float:
        """Calculate coherence score based on text quality."""
        all_text = f"{self.title} {self.summary} {self.problem} {self.solution}"

        # Simple coherence metrics
        sentences = [s.strip() for s in all_text.split('.') if len(s.strip()) > 10]
        if not sentences:
            return 0.0

        # Check for consistent terminology
        technical_terms = ['method', 'algorithm', 'approach', 'technique', 'framework']
        term_consistency = sum(1 for term in technical_terms if term.lower() in all_text.lower())

        return min(1.0, term_consistency / len(technical_terms))

    def _estimate_technical_depth(self) -> float:
        """Estimate technical depth of the analysis."""
        all_text = f"{self.solution} {self.key_contributions}"

        # Technical indicators
        technical_indicators = [
            'architecture', 'algorithm', 'framework', 'model', 'dataset',
            'accuracy', 'performance', 'efficiency', 'optimization', 'evaluation'
        ]

        found_indicators = sum(1 for indicator in technical_indicators
                             if indicator.lower() in all_text.lower())

        return min(1.0, found_indicators / len(technical_indicators))

    def get_total_word_count(self) -> int:
        """Get total word count of the analysis."""
        all_text = f"{self.title} {self.summary} {self.problem} {self.solution} {self.limitations} {self.key_contributions}"
        if self.research_significance:
            all_text += f" {self.research_significance}"
        return len(all_text.split())

    def is_valid(self) -> bool:
        """Check if analysis is valid and complete."""
        required_fields = [self.title, self.summary, self.problem, self.solution,
                          self.limitations, self.key_contributions]

        return all(field and len(field.strip()) > 10 for field in required_fields)

    def get_quality_score(self) -> float:
        """Get overall quality score."""
        return self.metrics.calculate_overall_score()

    def to_dict(self) -> Dict[str, Any]:
        """Convert analysis to dictionary."""
        return {
            'id': self.id,
            'paper_id': self.paper_id,
            'title': self.title,
            'summary': self.summary,
            'problem': self.problem,
            'solution': self.solution,
            'limitations': self.limitations,
            'key_contributions': self.key_contributions,
            'research_significance': self.research_significance,
            'status': self.status.value,
            'analysis_date': self.analysis_date.isoformat(),
            'metrics': {
                'confidence_score': self.metrics.confidence_score,
                'completeness_score': self.metrics.completeness_score,
                'coherence_score': self.metrics.coherence_score,
                'technical_depth_score': self.metrics.technical_depth_score,
                'word_count': self.metrics.word_count,
                'processing_time': self.metrics.processing_time,
                'token_count': self.metrics.token_count,
                'overall_score': self.get_quality_score()
            },
            'raw_response': self.raw_response,
            'error_message': self.error_message,
            'prompt_version': self.prompt_version,
            'model_used': self.model_used
        }

    def to_json(self) -> str:
        """Convert analysis to JSON string."""
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PaperAnalysis':
        """Create analysis from dictionary."""
        metrics_data = data.get('metrics', {})
        metrics = AnalysisMetrics(
            confidence_score=metrics_data.get('confidence_score', 0.0),
            completeness_score=metrics_data.get('completeness_score', 0.0),
            coherence_score=metrics_data.get('coherence_score', 0.0),
            technical_depth_score=metrics_data.get('technical_depth_score', 0.0),
            word_count=metrics_data.get('word_count', 0),
            processing_time=metrics_data.get('processing_time', 0.0),
            token_count=metrics_data.get('token_count', 0)
        )

        return cls(
            id=data['id'],
            paper_id=data['paper_id'],
            title=data['title'],
            summary=data['summary'],
            problem=data['problem'],
            solution=data['solution'],
            limitations=data['limitations'],
            key_contributions=data['key_contributions'],
            research_significance=data.get('research_significance'),
            status=AnalysisStatus(data.get('status', 'completed')),
            analysis_date=datetime.fromisoformat(data['analysis_date']),
            metrics=metrics,
            raw_response=data.get('raw_response'),
            error_message=data.get('error_message'),
            prompt_version=data.get('prompt_version', 'EN_2_0'),
            model_used=data.get('model_used', '')
        )