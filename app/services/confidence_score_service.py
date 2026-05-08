"""ConfidenceScoreService.

Computes a 0–100 confidence score from the margins between the top-ranked
candidate and its closest alternatives. A confident recommendation has a
clear winner; an uncertain one has tightly clustered scores.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.requests.recommendation_request import RecommendationRequest
    from app.services.recommendation_service import ScoredCandidate


class ConfidenceScoreService:
    def compute(
        self,
        languages: list["ScoredCandidate"],
        frameworks: list["ScoredCandidate"],
        sdlc: list["ScoredCandidate"],
        request: "RecommendationRequest",
    ) -> int:
        margin_l = self._margin(languages)
        margin_f = self._margin(frameworks)
        margin_s = self._margin(sdlc)

        # Weighted blend — language and framework matter most.
        margin = margin_l * 0.45 + margin_f * 0.35 + margin_s * 0.20

        # Slight boost when the request is fully specified.
        completeness = self._completeness_bonus(request)

        score = 55 + margin * 65 + completeness
        return max(35, min(99, int(round(score))))

    @staticmethod
    def _margin(candidates: list["ScoredCandidate"]) -> float:
        if len(candidates) < 2:
            return 0.5
        top = candidates[0].score
        runner = candidates[1].score
        if top <= 0:
            return 0.0
        return max(0.0, min(1.0, (top - runner) / top))

    @staticmethod
    def _completeness_bonus(request: "RecommendationRequest") -> float:
        fields = [
            request.project_name, request.project_type, request.project_goal,
            request.complexity, request.team_size, request.timeline,
            request.scalability, request.security, request.platform, request.experience,
        ]
        filled = sum(1 for f in fields if f)
        return (filled / len(fields)) * 6.0  # up to +6 points
