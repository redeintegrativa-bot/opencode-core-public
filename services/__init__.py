"""opencode-core services - decoupled crypto platform services."""

from .ranking_engine import configure as configure_ranking, score_all_opportunities
from .feedback_learning import configure as configure_feedback, submit_feedback

__all__ = [
    "configure_ranking",
    "configure_feedback",
    "score_all_opportunities",
    "submit_feedback",
]
