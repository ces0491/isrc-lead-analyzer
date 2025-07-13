"""
Core processing modules for lead generation pipeline
"""

# Import only what's needed to avoid circular imports
from .rate_limiter import RateLimitManager
from .scoring import LeadScoringEngine

# Import pipeline lazily to avoid circular dependency
def get_pipeline():
    """Get pipeline instance (lazy import)"""
    from .pipeline import LeadAggregationPipeline
    return LeadAggregationPipeline

__all__ = [
    'RateLimitManager',
    'LeadScoringEngine',
    'get_pipeline'
]
