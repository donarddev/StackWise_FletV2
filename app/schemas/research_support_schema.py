"""Research support schema definitions and input validation."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

COMMON_REQUIRED_FIELDS = [
    "research_title",
    "research_locale",
    "target_users",
    "academic_level",
]

COMMON_OPTIONAL_FIELDS = [
    "adviser_or_instructor",
    "institution_name",
    "additional_notes",
]

RESEARCH_TYPE_TEMPLATES: dict[str, dict[str, Any]] = {
    "Capstone Project Proposal": {
        "description": "Academic proposal for an applied IT/software capstone project.",
        "required_fields": [
            *COMMON_REQUIRED_FIELDS,
            "problem_background",
            "expected_output",
            "main_beneficiaries",
        ],
        "optional_fields": [*COMMON_OPTIONAL_FIELDS],
        "output_sections": [
            "title_page",
            "abstract",
            "introduction",
            "background_of_the_study",
            "statement_of_the_problem",
            "objectives_of_the_study",
            "scope_and_limitations",
            "significance_of_the_study",
            "proposed_system_overview",
            "methodology",
            "system_development_model",
            "recommended_technology_stack",
            "expected_output",
            "conclusion",
            "recommendations",
            "suggested_references_or_search_queries",
        ],
    },
    "System Development Research": {
        "description": "Research-oriented study on analyzing and improving an existing process through a proposed system.",
        "required_fields": [
            *COMMON_REQUIRED_FIELDS,
            "existing_system_or_current_process",
            "problems_encountered",
            "proposed_system_benefits",
        ],
        "optional_fields": [*COMMON_OPTIONAL_FIELDS],
        "output_sections": [
            "title_page",
            "abstract",
            "introduction",
            "existing_system_or_current_process",
            "proposed_system",
            "statement_of_the_problem",
            "objectives",
            "scope_and_limitations",
            "significance",
            "system_architecture_overview",
            "development_methodology",
            "technology_stack_justification",
            "testing_and_evaluation_plan",
            "conclusion",
            "recommendations",
            "suggested_references_or_search_queries",
        ],
    },
    "Software Requirements and Design Study": {
        "description": "Structured requirements engineering and design-oriented software study.",
        "required_fields": [
            *COMMON_REQUIRED_FIELDS,
            "stakeholders",
            "functional_requirements",
            "non_functional_requirements",
        ],
        "optional_fields": [*COMMON_OPTIONAL_FIELDS],
        "output_sections": [
            "title_page",
            "abstract",
            "introduction",
            "project_overview",
            "stakeholder_analysis",
            "functional_requirements",
            "non_functional_requirements",
            "use_case_overview",
            "data_requirements",
            "system_design_overview",
            "recommended_technology_stack",
            "sdlc_justification",
            "risk_and_constraint_analysis",
            "conclusion",
            "recommendations",
            "suggested_references_or_search_queries",
        ],
    },
    "Feasibility Study": {
        "description": "Study that evaluates technical, operational, economic, and schedule feasibility.",
        "required_fields": [
            *COMMON_REQUIRED_FIELDS,
            "available_resources",
            "estimated_timeline",
            "estimated_budget_or_constraints",
        ],
        "optional_fields": [*COMMON_OPTIONAL_FIELDS],
        "output_sections": [
            "title_page",
            "executive_summary",
            "introduction",
            "project_description",
            "technical_feasibility",
            "operational_feasibility",
            "economic_feasibility",
            "schedule_feasibility",
            "risk_analysis",
            "recommended_technology_stack",
            "implementation_considerations",
            "conclusion",
            "recommendations",
            "suggested_references_or_search_queries",
        ],
    },
    "AI / Machine Learning Research Proposal": {
        "description": "Proposal for an AI/ML-based project including dataset, evaluation, and ethics planning.",
        "required_fields": [
            *COMMON_REQUIRED_FIELDS,
            "dataset_source",
            "target_variable_or_output",
            "evaluation_metrics",
            "ethical_or_privacy_concerns",
        ],
        "optional_fields": [*COMMON_OPTIONAL_FIELDS],
        "output_sections": [
            "title_page",
            "abstract",
            "introduction",
            "background_of_the_study",
            "statement_of_the_problem",
            "objectives",
            "scope_and_limitations",
            "significance",
            "dataset_description",
            "proposed_ai_or_ml_approach",
            "model_development_methodology",
            "evaluation_metrics",
            "ethical_considerations",
            "expected_results",
            "conclusion",
            "recommendations",
            "suggested_references_or_search_queries",
        ],
    },
    "Comparative Technology Evaluation": {
        "description": "Comparative study to evaluate and justify technologies using weighted criteria.",
        "required_fields": [
            *COMMON_REQUIRED_FIELDS,
            "technologies_to_compare",
            "evaluation_criteria",
            "reason_for_comparison",
        ],
        "optional_fields": [*COMMON_OPTIONAL_FIELDS],
        "output_sections": [
            "title_page",
            "abstract",
            "introduction",
            "evaluation_problem",
            "objectives",
            "scope_and_limitations",
            "technology_candidates",
            "evaluation_criteria",
            "weighted_scoring_method",
            "comparison_results",
            "recommended_technology_stack",
            "discussion",
            "conclusion",
            "recommendations",
            "suggested_references_or_search_queries",
        ],
    },
    "Action Research for IT Solution": {
        "description": "Action research plan focused on iterative intervention and evaluation for IT solutions.",
        "required_fields": [
            *COMMON_REQUIRED_FIELDS,
            "problem_context",
            "participants_or_users",
            "intervention_plan",
            "evaluation_method",
        ],
        "optional_fields": [*COMMON_OPTIONAL_FIELDS],
        "output_sections": [
            "title_page",
            "abstract",
            "introduction",
            "problem_context",
            "action_research_objective",
            "participants_or_users",
            "intervention_or_proposed_system",
            "implementation_plan",
            "data_collection_plan",
            "evaluation_plan",
            "reflection_and_improvement_cycle",
            "conclusion",
            "recommendations",
            "suggested_references_or_search_queries",
        ],
    },
}


def get_research_type_template(research_type: str) -> dict[str, Any] | None:
    template = RESEARCH_TYPE_TEMPLATES.get(str(research_type or "").strip())
    return deepcopy(template) if template else None


def get_supported_research_types() -> list[str]:
    return list(RESEARCH_TYPE_TEMPLATES.keys())


def validate_research_inputs(research_type: str, research_inputs: dict[str, Any] | None) -> dict[str, Any]:
    template = RESEARCH_TYPE_TEMPLATES.get(str(research_type or "").strip())
    if not template:
        return {
            "success": False,
            "missing_fields": [],
            "error": f"Unsupported research type: {research_type}",
        }

    payload = research_inputs if isinstance(research_inputs, dict) else {}
    missing_fields = [
        field
        for field in template["required_fields"]
        if str(payload.get(field, "") or "").strip() == ""
    ]

    return {
        "success": len(missing_fields) == 0,
        "missing_fields": missing_fields,
    }
