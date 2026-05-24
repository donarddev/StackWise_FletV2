"""Map Phase 1 engine output keys for persistence and UI (no scoring logic)."""

from __future__ import annotations

from typing import Any


def risks_as_display_strings(engine_result: dict[str, Any]) -> list[str]:
    """Backward-compatible risk lines from ``risks`` or structured ``risk_analysis``."""
    legacy = engine_result.get("risks")
    if isinstance(legacy, list) and legacy:
        return [str(v).strip() for v in legacy if str(v).strip()]

    items = engine_result.get("risk_analysis") or []
    if not isinstance(items, list):
        return []

    lines: list[str] = []
    for item in items:
        if isinstance(item, dict):
            risk = str(item.get("risk", "") or "").strip()
            reason = str(item.get("reason", "") or "").strip()
            if risk and reason:
                lines.append(f"{risk}: {reason}")
            elif risk:
                lines.append(risk)
        elif str(item).strip():
            lines.append(str(item).strip())
    return lines


def skill_gaps_as_display_strings(engine_result: dict[str, Any]) -> list[str]:
    """Backward-compatible skill gap lines from ``skill_gaps`` or ``skill_gap_analysis``."""
    legacy = engine_result.get("skill_gaps")
    if isinstance(legacy, list) and legacy:
        return [str(v).strip() for v in legacy if str(v).strip()]

    items = engine_result.get("skill_gap_analysis") or []
    if not isinstance(items, list):
        return []

    lines: list[str] = []
    for item in items:
        if isinstance(item, dict):
            skill = str(item.get("skill", "") or "").strip()
            suggestion = str(item.get("suggestion", "") or "").strip()
            gap = str(item.get("gap_level", "") or "").strip()
            if skill and suggestion:
                prefix = f"{skill} ({gap} gap): " if gap else f"{skill}: "
                lines.append(prefix + suggestion)
            elif skill:
                lines.append(skill)
        elif str(item).strip():
            lines.append(str(item).strip())
    return lines


def roadmap_source(engine_result: dict[str, Any]) -> Any:
    return engine_result.get("suggested_project_roadmap") or engine_result.get("roadmap")


def alternative_stacks_from_record(
    explanation: dict[str, Any] | None,
    alternatives: dict[str, Any] | None,
) -> list[dict[str, Any]]:
    """Extract stack-based alternatives from a saved recommendation record."""
    expl = explanation if isinstance(explanation, dict) else {}
    alts = alternatives if isinstance(alternatives, dict) else {}

    stacks = expl.get("alternative_technology_stacks")
    if isinstance(stacks, list) and stacks:
        return [s for s in stacks if isinstance(s, dict)]

    stacks = alts.get("technology_stacks")
    if isinstance(stacks, list) and stacks:
        return [s for s in stacks if isinstance(s, dict)]

    engine = expl.get("engine_full_result")
    if isinstance(engine, dict):
        stacks = engine.get("alternative_technology_stacks")
        if isinstance(stacks, list) and stacks:
            return [s for s in stacks if isinstance(s, dict)]

    legacy = alts.get("alternatives")
    if isinstance(legacy, list) and legacy and isinstance(legacy[0], dict):
        if legacy[0].get("language") and legacy[0].get("framework"):
            return [s for s in legacy if isinstance(s, dict)]

    return []


def format_alternative_fit_display(alt: dict[str, Any]) -> str:
    """Human-readable fit label; never show raw internal point totals."""
    display = str(alt.get("fit_display", "") or "").strip()
    if display:
        return display

    for key in ("fit_percent", "fit_score"):
        raw = alt.get(key)
        if raw is None:
            continue
        try:
            value = float(raw)
        except (TypeError, ValueError):
            continue
        if value > 100:
            pct = max(60, min(95, 60 + round(value / 15)))
        else:
            pct = int(round(value))
        pct = max(60, min(95, pct))
        return "Strong fit" if pct >= 88 else f"{pct}% Fit"

    return ""


def format_alternative_stack_title(alt: dict[str, Any]) -> str:
    """Stack title; DevOps is not shown as the primary SDLC segment."""
    lang = str(alt.get("language", "") or "").strip()
    fw = str(alt.get("framework", "") or "").strip()
    sdlc = str(alt.get("sdlc", "") or "").strip()
    parts = [p for p in (lang, fw) if p]
    if sdlc and sdlc != "DevOps":
        parts.append(sdlc)
    return " + ".join(parts) if parts else "Alternative stack"


def devops_support_note(alt: dict[str, Any]) -> str | None:
    if str(alt.get("sdlc", "") or "").strip() == "DevOps":
        return (
            "DevOps support for CI/CD, monitoring, cloud deployment, and maintenance."
        )
    limitation = str(alt.get("limitation", "") or "")
    if "devops practices are recommended" in limitation.lower():
        return (
            "DevOps support for CI/CD, monitoring, cloud deployment, and maintenance."
        )
    return None


def engine_full_result_from_explanation(explanation: dict[str, Any] | None) -> dict[str, Any]:
    """Embedded engine snapshot on saved rows (structured arrays)."""
    expl = explanation if isinstance(explanation, dict) else {}
    snap = expl.get("engine_full_result")
    return snap if isinstance(snap, dict) else {}


def structured_risk_analysis(source: dict[str, Any]) -> list[dict[str, Any]]:
    """Risk cards for UI; prefers structured ``risk_analysis`` over legacy strings."""
    items = source.get("risk_analysis")
    if isinstance(items, list) and items:
        if items and isinstance(items[0], dict):
            return [i for i in items if isinstance(i, dict)]
        rows: list[dict[str, Any]] = []
        for item in items:
            text = str(item).strip()
            if not text:
                continue
            if ":" in text:
                risk, reason = text.split(":", 1)
                rows.append(
                    {
                        "risk": risk.strip(),
                        "reason": reason.strip(),
                        "impact": "Medium",
                        "mitigation": reason.strip(),
                    }
                )
            else:
                rows.append(
                    {
                        "risk": text,
                        "reason": "",
                        "impact": "Medium",
                        "mitigation": "Review scope and mitigate early.",
                    }
                )
        return rows

    legacy = source.get("risks") or []
    rows = []
    for item in legacy:
        text = str(item).strip()
        if not text:
            continue
        if ":" in text:
            risk, reason = text.split(":", 1)
            rows.append(
                {
                    "risk": risk.strip(),
                    "reason": reason.strip(),
                    "impact": "Medium",
                    "mitigation": reason.strip(),
                }
            )
        else:
            rows.append(
                {
                    "risk": text,
                    "reason": "",
                    "impact": "Medium",
                    "mitigation": "Review scope and mitigate early.",
                }
            )
    return rows


def structured_skill_gap_analysis(source: dict[str, Any]) -> list[dict[str, Any]]:
    """Skill gap rows for table UI."""
    items = source.get("skill_gap_analysis")
    if isinstance(items, list) and items:
        if items and isinstance(items[0], dict):
            return [i for i in items if isinstance(i, dict)]
        rows: list[dict[str, Any]] = []
        for item in items:
            text = str(item).strip()
            if not text:
                continue
            if ":" in text:
                skill, rest = text.split(":", 1)
                rows.append(
                    {
                        "skill": skill.strip(),
                        "required_level": "—",
                        "user_level": "—",
                        "gap_level": "—",
                        "suggestion": rest.strip(),
                    }
                )
            else:
                rows.append(
                    {
                        "skill": text,
                        "required_level": "—",
                        "user_level": "—",
                        "gap_level": "—",
                        "suggestion": "",
                    }
                )
        return rows

    legacy = source.get("skill_gaps") or []
    rows = []
    for item in legacy:
        text = str(item).strip()
        if not text:
            continue
        rows.append(
            {
                "skill": text,
                "required_level": "—",
                "user_level": "—",
                "gap_level": "—",
                "suggestion": "",
            }
        )
    return rows


def structured_roadmap_phases(source: dict[str, Any]) -> list[dict[str, Any]]:
    """Roadmap phase dicts for grid cards."""
    raw = roadmap_source(source)
    if not isinstance(raw, list):
        return []

    phases: list[dict[str, Any]] = []
    for item in raw:
        if isinstance(item, dict):
            phases.append(item)
        elif str(item).strip():
            text = str(item).strip()
            if ":" in text:
                title, desc = text.split(":", 1)
                phases.append(
                    {
                        "phase": str(len(phases) + 1),
                        "title": title.strip(),
                        "description": desc.strip(),
                        "objectives": [],
                        "deliverables": [],
                        "priorities": [],
                    }
                )
            else:
                phases.append(
                    {
                        "phase": str(len(phases) + 1),
                        "title": text,
                        "description": "",
                        "objectives": [],
                        "deliverables": [],
                        "priorities": [],
                    }
                )
    return phases


def why_not_entries_sorted(entries: list[Any]) -> list[dict[str, Any]]:
    """User preferred stack explanations appear first."""
    if not isinstance(entries, list):
        return []
    rows = [e for e in entries if isinstance(e, dict)]
    preferred = [e for e in rows if str(e.get("source", "")).strip() == "User Preferred Stack"]
    other = [e for e in rows if str(e.get("source", "")).strip() != "User Preferred Stack"]
    return preferred + other


def normalize_engine_result_for_ui(result: dict[str, Any] | None) -> dict[str, Any]:
    """Ensure legacy alias keys exist so details/session pages do not crash."""
    if not result:
        return {}
    out = dict(result)
    if not out.get("alternatives") and out.get("alternative_technology_stacks"):
        out["alternatives"] = out["alternative_technology_stacks"]
    if not out.get("risks"):
        out["risks"] = risks_as_display_strings(out)
    if not out.get("skill_gaps"):
        out["skill_gaps"] = skill_gaps_as_display_strings(out)
    if not out.get("roadmap"):
        out["roadmap"] = roadmap_source(out)
    return out
