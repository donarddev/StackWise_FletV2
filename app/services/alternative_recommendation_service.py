"""AlternativeRecommendationService.

Builds the structured alternatives payload for storage and UI.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.services.recommendation_orchestrator_service import ScoredCandidate


class AlternativeRecommendationService:
    TOP_N = 3

    def build(
        self,
        language_candidates: list["ScoredCandidate"],
        framework_candidates: list["ScoredCandidate"],
        sdlc_candidates: list["ScoredCandidate"],
    ) -> dict:
        return {
            "languages": [self._serialize(c) for c in language_candidates[: self.TOP_N + 1]],
            "frameworks": [self._serialize(c) for c in framework_candidates[: self.TOP_N + 1]],
            "sdlc": [self._serialize(c) for c in sdlc_candidates[: self.TOP_N + 1]],
        }

    @staticmethod
    def _serialize(c: "ScoredCandidate") -> dict:
        return {"name": c.name, "score": c.score, "rationale": list(c.rationale)}
