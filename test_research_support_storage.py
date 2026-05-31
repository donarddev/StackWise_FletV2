"""Research Support Assistant storage smoke test.

Run from project root:
    python test_research_support_storage.py
"""

from __future__ import annotations

from app.config.database_config import get_database_config
from app.repositories.research_output_repository import ResearchOutputRepository
from app.services.database_service import DatabaseService
from app.services.research_support_service import ResearchSupportService


def _assert(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> None:
    db = DatabaseService(get_database_config())
    db.connect()

    repo = ResearchOutputRepository(db)
    service = ResearchSupportService(repo)

    table_result = repo.create_table_if_not_exists()
    _assert(table_result.get("success") is True, f"Table creation failed: {table_result}")
    print("Research output table ready.")

    types_result = service.get_supported_research_types()
    _assert(types_result.get("success") is True, "Supported research types failed to load.")
    supported_types = types_result.get("data") or []
    _assert("Capstone Project Proposal" in supported_types, "Capstone type missing.")
    _assert("Feasibility Study" in supported_types, "Feasibility type missing.")
    print("Supported research types loaded.")

    recommendation_data = {
        "project_name": "StackWise Student Project Assistant",
        "project_type": "Web Application",
        "recommended_language": "Python",
        "recommended_framework": "Flet",
        "recommended_sdlc": "Agile",
        "confidence_score": 86,
    }

    project_data = {
        "project_goal": "Support students in selecting practical software stacks for capstone projects.",
        "selected_features": [
            "Authentication",
            "Role-based Access",
            "Recommendation Engine",
            "Report Generation",
        ],
        "complexity": "Medium",
        "timeline": "4 months",
        "preferred_platform": "Web",
        "security_requirements": "Medium",
        "performance_requirements": "Medium",
        "deployment_preference": "Cloud",
    }

    recommendation_id = 910001
    user_id = 1

    capstone_inputs = {
        "research_title": "StackWise AI for Student Software Stack Decision Support",
        "research_locale": "Philippines",
        "target_users": "IT and Computer Science students",
        "academic_level": "Undergraduate",
        "problem_background": "Students often choose technology stacks without structured evaluation.",
        "expected_output": "A recommendation platform with rationale and research support draft.",
        "main_beneficiaries": "Students, advisers, and capstone panels.",
    }

    invalid_validation = service.validate_research_request(
        "Capstone Project Proposal",
        {
            "research_title": "Incomplete Input",
            "research_locale": "PH",
        },
    )
    _assert(invalid_validation.get("success") is False, "Missing field validation should fail.")
    _assert(len(invalid_validation.get("missing_fields") or []) > 0, "Missing fields should be returned.")

    capstone_build = service.build_dummy_research_output(
        recommendation_data,
        project_data,
        "Capstone Project Proposal",
        capstone_inputs,
    )
    _assert(capstone_build.get("success") is True, f"Capstone dummy build failed: {capstone_build}")

    capstone_save = service.save_research_output(recommendation_id, user_id, capstone_build["data"])
    _assert(capstone_save.get("success") is True, f"Capstone save failed: {capstone_save}")
    print("Capstone dummy research output saved.")

    capstone_get = service.get_research_output(recommendation_id, user_id)
    _assert(capstone_get.get("success") is True, f"Capstone retrieval failed: {capstone_get}")
    _assert(capstone_get.get("data") is not None, "Capstone record not found after save.")
    print("Capstone output retrieved successfully.")

    capstone_data = capstone_get["data"]
    draft_keys = list((capstone_data.get("research_draft") or {}).keys())
    print(f"research_type: {capstone_data.get('research_type')}")
    print(f"research_title: {capstone_data.get('research_title')}")
    print(f"draft_section_keys: {draft_keys}")
    print(f"suggested_journals_count: {len(capstone_data.get('suggested_journals') or [])}")
    print(f"search_links_count: {len(capstone_data.get('open_access_links') or [])}")
    print(
        "publication_recommended_level: "
        f"{(capstone_data.get('publication_recommendation') or {}).get('recommended_level')}"
    )

    feasibility_inputs = {
        "research_title": "Feasibility Assessment of StackWise Deployment",
        "research_locale": "Philippines",
        "target_users": "Academic departments and student developers",
        "academic_level": "Undergraduate",
        "available_resources": "Existing web hosting, faculty mentorship, and student developer team.",
        "estimated_timeline": "One semester",
        "estimated_budget_or_constraints": "Low budget with reliance on open-source tools.",
    }

    feasibility_build = service.build_dummy_research_output(
        recommendation_data,
        project_data,
        "Feasibility Study",
        feasibility_inputs,
    )
    _assert(feasibility_build.get("success") is True, f"Feasibility dummy build failed: {feasibility_build}")

    feasibility_save = service.save_research_output(recommendation_id + 1, user_id, feasibility_build["data"])
    _assert(feasibility_save.get("success") is True, f"Feasibility save failed: {feasibility_save}")
    print("Feasibility dummy research output saved.")

    feasibility_get = service.get_research_output(recommendation_id + 1, user_id)
    _assert(feasibility_get.get("success") is True, f"Feasibility retrieval failed: {feasibility_get}")
    _assert(feasibility_get.get("data") is not None, "Feasibility record not found after save.")

    feasibility_draft = (feasibility_get["data"] or {}).get("research_draft") or {}
    _assert("technical_feasibility" in feasibility_draft, "Feasibility output missing technical_feasibility section.")
    _assert("economic_feasibility" in feasibility_draft, "Feasibility output missing economic_feasibility section.")
    print("Feasibility output retrieved successfully.")

    print("All research support storage tests passed.")


if __name__ == "__main__":
    main()
