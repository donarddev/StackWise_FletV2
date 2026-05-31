"""Persist Phase 1 engine results to MySQL (no scoring logic).

Maps engine input/output dicts into the storage shape expected by
``RecommendationRepository`` and the recommendation result UI.
"""

from __future__ import annotations

import re
from typing import Any, TYPE_CHECKING

from app.helpers.recommendation_engine_compat import (
    risks_as_display_strings,
    roadmap_source,
    skill_gaps_as_display_strings,
)
from app.models.recommendation import Recommendation
from app.utils.logger import get_logger

if TYPE_CHECKING:
    from app.repositories.recommendation_repository import RecommendationRepository

log = get_logger(__name__)

_EXPLANATION_MARKERS = (
    ("why_language", "Why this language", "Language:"),
    ("why_framework", "Why this framework", "Framework:"),
    ("why_sdlc", "Why this SDLC model", "SDLC:"),
)


class RecommendationPersistenceService:
    def __init__(self, recommendation_repository: "RecommendationRepository") -> None:
        self._repo = recommendation_repository

    def save_engine_result(
        self,
        user_id: int,
        input_data: dict[str, Any],
        engine_result: dict[str, Any],
    ) -> Recommendation:
        """Insert a new recommendation row from engine payloads."""
        request_payload = build_request_payload(input_data)
        result_payload = build_result_payload(engine_result)
        try:
            rec = self._repo.create(user_id, request_payload, result_payload)
        except Exception:
            log.exception("Failed to save recommendation for user_id=%s", user_id)
            raise
        if rec is None:
            raise RuntimeError("Recommendation was not returned after insert.")
        _verify_saved_matches_engine(rec, engine_result)
        return rec

    @staticmethod
    def input_data_from_recommendation(rec: Recommendation) -> dict[str, Any]:
        """Rebuild engine request dict from a saved row (for regenerate)."""
        profile = rec.project_profile or {}
        features = profile.get("selected_features", [])
        if isinstance(features, str):
            features = [
                f.strip()
                for f in features.replace("|", ",").split(",")
                if f.strip()
            ]
        elif not isinstance(features, list):
            features = []

        return {
            "project_name": rec.project_name,
            "project_type": rec.project_type,
            "selected_features": features,
            "project_goal": profile.get("project_goal") or rec.project_goal,
            "team_size": rec.team_size,
            "complexity": rec.complexity,
            "timeline": rec.timeline,
            "requirements_stability": profile.get(
                "requirements_stability", "Mostly Stable"
            ),
            "stakeholder_involvement": profile.get(
                "stakeholder_involvement", "Medium"
            ),
            "preferred_platform": profile.get("preferred_platform") or rec.platform,
            "development_experience": profile.get("development_experience")
            or rec.experience,
            "scalability_needs": profile.get("scalability_needs") or rec.scalability,
            "performance_requirements": profile.get(
                "performance_requirements", "Medium"
            ),
            "security_requirements": profile.get("security_requirements")
            or rec.security,
            "budget_constraints": profile.get("budget_constraints", "Medium"),
            "maintenance_expectations": profile.get(
                "maintenance_expectations", "Medium"
            ),
            "deployment_preference": profile.get(
                "deployment_preference", "Cloud"
            ),
            "user_preferred_language": profile.get("user_preferred_language", ""),
            "user_preferred_framework": profile.get("user_preferred_framework", ""),
            "user_preferred_sdlc": profile.get("user_preferred_sdlc", ""),
            "user_preferred_reason": profile.get("user_preferred_reason", ""),
        }


def build_request_payload(input_data: dict[str, Any]) -> dict[str, Any]:
    """Normalize form/engine input for repository columns + project_profile_json."""
    features = input_data.get("selected_features", [])
    if isinstance(features, str):
        features = [
            f.strip()
            for f in features.replace("|", ",").split(",")
            if f.strip()
        ]
    elif not isinstance(features, list):
        features = []

    team_raw = input_data.get("team_size", "1")
    team_size = str(team_raw).strip() if team_raw is not None else "1"

    return {
        "project_name": str(input_data.get("project_name", "") or "").strip(),
        "project_type": str(input_data.get("project_type", "") or "").strip(),
        "project_goal": str(input_data.get("project_goal", "") or "").strip(),
        "team_size": team_size or "1",
        "complexity": str(input_data.get("complexity", "") or "Medium").strip(),
        "timeline": str(input_data.get("timeline", "") or "Medium").strip(),
        "scalability_needs": str(
            input_data.get("scalability_needs", "") or "Medium"
        ).strip(),
        "security_requirements": str(
            input_data.get("security_requirements", "") or "Medium"
        ).strip(),
        "preferred_platform": str(
            input_data.get("preferred_platform", "") or "Web"
        ).strip(),
        "development_experience": str(
            input_data.get("development_experience", "") or "Intermediate"
        ).strip(),
        "selected_features": features,
        "requirements_stability": str(
            input_data.get("requirements_stability", "") or "Mostly Stable"
        ).strip(),
        "stakeholder_involvement": str(
            input_data.get("stakeholder_involvement", "") or "Medium"
        ).strip(),
        "performance_requirements": str(
            input_data.get("performance_requirements", "") or "Medium"
        ).strip(),
        "budget_constraints": str(
            input_data.get("budget_constraints", "") or "Medium"
        ).strip(),
        "maintenance_expectations": str(
            input_data.get("maintenance_expectations", "") or "Medium"
        ).strip(),
        "deployment_preference": str(
            input_data.get("deployment_preference", "") or "Cloud"
        ).strip(),
        "user_preferred_language": str(
            input_data.get("user_preferred_language", "") or ""
        ).strip(),
        "user_preferred_framework": str(
            input_data.get("user_preferred_framework", "") or ""
        ).strip(),
        "user_preferred_sdlc": str(
            input_data.get("user_preferred_sdlc", "") or ""
        ).strip(),
        "user_preferred_reason": str(
            input_data.get("user_preferred_reason", "") or ""
        ).strip(),
    }


def attach_saved_recommendation_id(result: dict[str, Any], saved_id: int) -> dict[str, Any]:
    """Attach saved database ID aliases to an engine result payload."""
    out = dict(result or {})
    out["id"] = saved_id
    out["recommendation_id"] = saved_id
    out["record_id"] = saved_id

    saved = out.get("saved_recommendation")
    if isinstance(saved, dict):
        saved_obj = dict(saved)
    else:
        saved_obj = {}
    saved_obj["id"] = saved_id
    saved_obj["recommendation_id"] = saved_id
    saved_obj["record_id"] = saved_id
    out["saved_recommendation"] = saved_obj
    return out


def build_result_payload(engine_result: dict[str, Any]) -> dict[str, Any]:
    """Map engine ``RecommendationResult.to_dict()`` into repository result shape."""
    score_raw = engine_result.get("confidence_score", 0)
    try:
        confidence_score = int(round(float(score_raw)))
    except (TypeError, ValueError):
        confidence_score = 0
    confidence_score = max(0, min(100, confidence_score))

    explanation = _build_explanation_document(engine_result)
    alternatives = _build_alternatives_document(engine_result)

    return {
        "recommended_language": str(
            engine_result.get("recommended_language", "") or ""
        ),
        "recommended_framework": str(
            engine_result.get("recommended_framework", "") or ""
        ),
        "recommended_sdlc": str(engine_result.get("recommended_sdlc", "") or ""),
        "confidence_score": confidence_score,
        "confidence_label": str(engine_result.get("confidence_label", "") or ""),
        "explanation": explanation,
        "alternatives": alternatives,
        "full_result": engine_result,
    }


def _build_explanation_document(engine_result: dict[str, Any]) -> dict[str, Any]:
    raw = str(engine_result.get("explanation", "") or "").strip()
    summary, why_sections = _parse_engine_explanation_text(raw)

    explanation: dict[str, Any] = {
        "summary": summary or raw,
        "risk_analysis": risks_as_display_strings(engine_result),
        "skill_gap_analysis": skill_gaps_as_display_strings(engine_result),
        "roadmap": _roadmap_as_strings(roadmap_source(engine_result)),
        "trade_offs": [],
        "scoring_basis": str(engine_result.get("scoring_basis", "") or ""),
        "defense_explanation": str(engine_result.get("defense_explanation", "") or ""),
        "validation_note": str(engine_result.get("validation_note", "") or ""),
        "language_reason": str(engine_result.get("language_reason", "") or ""),
        "framework_reason": str(engine_result.get("framework_reason", "") or ""),
        "sdlc_reason": str(engine_result.get("sdlc_reason", "") or ""),
        "why_not_this": engine_result.get("why_not_this") or [],
        "user_preferred_stack": engine_result.get("user_preferred_stack") or {},
        "alternative_technology_stacks": engine_result.get("alternative_technology_stacks")
        or [],
        "engine_full_result": engine_result,
    }

    for key, title, _prefix in _EXPLANATION_MARKERS:
        paragraph = why_sections.get(key, "")
        if paragraph:
            explanation[key] = {
                "title": title,
                "points": _paragraph_to_points(paragraph),
            }

    explanation["why_not_languages"] = _alt_runners(
        engine_result.get("alternative_languages")
    )
    explanation["why_not_frameworks"] = _alt_runners(
        engine_result.get("alternative_frameworks")
    )
    explanation["why_not_sdlc"] = _alt_runners(engine_result.get("alternative_sdlc_models"))

    return explanation


def _build_alternatives_document(engine_result: dict[str, Any]) -> dict[str, Any]:
    stacks = engine_result.get("alternative_technology_stacks") or []
    if not isinstance(stacks, list):
        stacks = []
    return {
        "languages": _alt_scores(engine_result.get("language_scores")),
        "frameworks": _alt_scores(engine_result.get("framework_scores")),
        "sdlc": _alt_scores(engine_result.get("sdlc_scores")),
        "technology_stacks": stacks,
        "runners_up": {
            "languages": engine_result.get("alternative_languages") or [],
            "frameworks": engine_result.get("alternative_frameworks") or [],
            "sdlc": engine_result.get("alternative_sdlc_models") or [],
        },
    }


def _parse_engine_explanation_text(text: str) -> tuple[str, dict[str, str]]:
    if not text:
        return "", {}

    whys: dict[str, str] = {}
    summary_parts: list[str] = []
    prefix_to_key = {prefix: key for key, _title, prefix in _EXPLANATION_MARKERS}

    for block in re.split(r"\n\s*\n", text):
        block = block.strip()
        if not block:
            continue
        matched = False
        for prefix, key in prefix_to_key.items():
            if block.startswith(prefix):
                whys[key] = block
                matched = True
                break
        if not matched:
            summary_parts.append(block)

    return "\n\n".join(summary_parts).strip(), whys


def _paragraph_to_points(paragraph: str) -> list[str]:
    lines = [ln.strip() for ln in paragraph.split("\n") if ln.strip()]
    if len(lines) <= 1:
        return [paragraph.strip()] if paragraph.strip() else []
    return lines


def _alt_runners(items: Any) -> list[dict[str, str]]:
    if not isinstance(items, list):
        return []
    runners: list[dict[str, str]] = []
    for item in items[:4]:
        if not isinstance(item, dict):
            continue
        name = str(item.get("name", "") or "").strip()
        if not name:
            continue
        reason = str(item.get("reason", "") or "").strip()
        if not reason and item.get("score") is not None:
            reason = f"Score {item.get('score')} — alternative for this profile."
        runners.append({"name": name, "reason": reason or "Runner-up for this profile."})
    return runners


def _alt_scores(scores: Any) -> list[dict[str, Any]]:
    if not isinstance(scores, dict):
        return []
    ranked = sorted(scores.items(), key=lambda kv: float(kv[1] or 0), reverse=True)
    return [{"name": name, "score": score} for name, score in ranked[:6]]


def _as_str_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(v).strip() for v in value if str(v).strip()]


def _verify_saved_matches_engine(rec: Recommendation, engine_result: dict[str, Any]) -> None:
    """Log when DB columns diverge from the engine output (should not happen)."""
    pairs = (
        ("recommended_language", "recommended_language"),
        ("recommended_framework", "recommended_framework"),
        ("recommended_sdlc", "recommended_sdlc"),
        ("confidence_score", "confidence_score"),
    )
    for db_attr, engine_key in pairs:
        saved_val = getattr(rec, db_attr, None)
        engine_val = engine_result.get(engine_key)
        if engine_key == "confidence_score":
            try:
                engine_val = int(round(float(engine_val or 0)))
            except (TypeError, ValueError):
                engine_val = 0
        if str(saved_val) != str(engine_val):
            log.warning(
                "Saved recommendation id=%s mismatch %s: db=%r engine=%r",
                rec.id,
                db_attr,
                saved_val,
                engine_val,
            )


def apply_engine_snapshot_to_recommendation(rec: Recommendation) -> Recommendation:
    """Overlay DB row with embedded engine snapshot when present (display/history sync)."""
    expl = rec.explanation or {}
    snap = expl.get("engine_full_result")
    if not isinstance(snap, dict) or not snap:
        return rec
    rec.recommended_language = str(
        snap.get("recommended_language", rec.recommended_language) or rec.recommended_language
    )
    rec.recommended_framework = str(
        snap.get("recommended_framework", rec.recommended_framework) or rec.recommended_framework
    )
    rec.recommended_sdlc = str(
        snap.get("recommended_sdlc", rec.recommended_sdlc) or rec.recommended_sdlc
    )
    try:
        rec.confidence_score = int(round(float(snap.get("confidence_score", rec.confidence_score))))
    except (TypeError, ValueError):
        pass
    rec.confidence_score = max(0, min(100, rec.confidence_score))
    return rec


def _roadmap_as_strings(roadmap: Any) -> list[str]:
    if not isinstance(roadmap, list) or not roadmap:
        return []
    lines: list[str] = []
    for item in roadmap:
        if isinstance(item, dict):
            title = str(item.get("title", "") or "").strip()
            desc = str(item.get("description", "") or "").strip()
            phase = str(item.get("phase", "") or "").strip()
            if title and desc:
                lines.append(f"{title}: {desc}")
            elif title:
                lines.append(title)
            elif desc:
                lines.append(desc)
            elif phase:
                lines.append(f"Phase {phase}")
        elif str(item).strip():
            lines.append(str(item).strip())
    return lines
