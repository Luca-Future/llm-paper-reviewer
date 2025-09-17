"""
Core exceptions for the paper analysis system.
"""


class PaperAnalysisError(Exception):
    """Base exception for paper analysis errors."""
    pass


class AnalysisConfigurationError(PaperAnalysisError):
    """Exception raised when analysis configuration is invalid."""
    pass


class AIServiceError(PaperAnalysisError):
    """Exception raised when AI service encounters an error."""
    pass


class PaperParseError(PaperAnalysisError):
    """Exception raised when paper parsing fails."""
    pass


class ValidationError(PaperAnalysisError):
    """Exception raised when validation fails."""
    pass