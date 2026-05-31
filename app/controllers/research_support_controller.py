"""Controller facade for Research Support Assistant backend logic."""

from __future__ import annotations

from typing import Any, Optional

from app.config.database_config import get_database_config
from app.repositories.research_output_repository import ResearchOutputRepository
from app.services.database_service import DatabaseService
from app.services.research_support_service import ResearchSupportService
from app.utils.logger import get_logger

log = get_logger(__name__)

_db_service: DatabaseService | None = None
_service: ResearchSupportService | None = None


def _get_service() -> ResearchSupportService:
    global _db_service, _service
    if _service is not None:
        return _service

    if _db_service is None:
        _db_service = DatabaseService(get_database_config())
        _db_service.connect()

    repository = ResearchOutputRepository(_db_service)
    repository.create_table_if_not_exists()
    _service = ResearchSupportService(repository)
    return _service


def get_supported_research_types() -> dict[str, Any]:
    try:
        return _get_service().get_supported_research_types()
    except Exception as exc:
        log.exception("get_supported_research_types failed")
        return {"success": False, "error": str(exc)}


def get_research_type_details(research_type: str) -> dict[str, Any]:
    try:
        return _get_service().get_research_type_template(research_type)
    except Exception as exc:
        log.exception("get_research_type_details failed research_type=%s", research_type)
        return {"success": False, "error": str(exc)}


def validate_research_inputs(research_type: str, research_inputs: dict[str, Any]) -> dict[str, Any]:
    try:
        return _get_service().validate_research_request(research_type, research_inputs)
    except Exception as exc:
        log.exception("validate_research_inputs failed research_type=%s", research_type)
        return {"success": False, "error": str(exc)}


def generate_dummy_research_support_for_recommendation(
    recommendation_id: int,
    user_id: Optional[int],
    recommendation_data: dict[str, Any],
    project_data: dict[str, Any],
    research_type: str,
    research_inputs: dict[str, Any],
) -> dict[str, Any]:
    try:
        project_name = str(project_data.get("project_name") or recommendation_data.get("project_name") or "")
        research_title = str(research_inputs.get("research_title") or project_name or "")
        print("Research Support generation:")
        print(f"recommendation_id = {recommendation_id}")
        print(f"project_name = {project_name}")
        print(f"research_type = {research_type}")
        print(f"research_title = {research_title}")

        service = _get_service()
        output_result = service.build_dummy_research_output(
            recommendation_data,
            project_data,
            research_type,
            research_inputs,
        )
        if not output_result.get("success"):
            return output_result

        return service.save_research_output(
            recommendation_id,
            user_id,
            output_result["data"],
        )
    except Exception as exc:
        log.exception(
            "generate_dummy_research_support_for_recommendation failed recommendation_id=%s user_id=%s",
            recommendation_id,
            user_id,
        )
        return {"success": False, "error": str(exc)}


def generate_template_research_support_for_recommendation(
    recommendation_id: int,
    user_id: Optional[int],
    recommendation_data: dict[str, Any],
    project_data: dict[str, Any],
    research_type: str,
    research_inputs: dict[str, Any],
) -> dict[str, Any]:
    return generate_dummy_research_support_for_recommendation(
        recommendation_id,
        user_id,
        recommendation_data,
        project_data,
        research_type,
        research_inputs,
    )


def generate_ai_research_support_for_recommendation(
    recommendation_id: int,
    user_id: Optional[int],
    recommendation_data: dict[str, Any],
    project_data: dict[str, Any],
    research_type: str,
    research_inputs: dict[str, Any],
) -> dict[str, Any]:
    try:
        project_name = str(project_data.get("project_name") or recommendation_data.get("project_name") or "")
        research_title = str(research_inputs.get("research_title") or project_name or "")
        service = _get_service()
        config = service._ollama.config
        print("Research Support generation (Ollama):")
        print(f"recommendation_id = {recommendation_id}")
        print(f"research_type = {research_type}")
        print(f"research_title = {research_title}")
        print(f"ollama_base_url = {config.base_url}")
        print(f"ollama_model = {config.model}")

        health = service.check_ollama_available()
        print(f"ollama_available = {bool(health.get('success'))}")
        print(f"model_found = {bool(health.get('model_found'))}")
        if not health.get("success"):
            return {
                "success": False,
                "error": str(health.get("error") or "Ollama is not running or unreachable."),
                "error_type": str(health.get("error_type") or "unreachable"),
                "models": health.get("models") or [],
                "fallback_available": True,
            }

        generated_result = service.generate_ai_research_support(
            recommendation_id,
            recommendation_data,
            project_data,
            research_type,
            research_inputs,
        )
        if not generated_result.get("success"):
            return {
                "success": False,
                "error": str(generated_result.get("error") or "Research generation failed."),
                "error_type": str(generated_result.get("error_type") or "unknown"),
                "fallback_available": True,
                "models": generated_result.get("models") or health.get("models") or [],
            }

        saved_result = service.save_research_output(
            recommendation_id,
            user_id,
            generated_result["data"],
        )
        if saved_result.get("success"):
            saved_result["data"] = saved_result.get("data") or generated_result.get("data")
        return saved_result
    except Exception as exc:
        log.exception(
            "generate_ai_research_support_for_recommendation failed recommendation_id=%s user_id=%s",
            recommendation_id,
            user_id,
        )
        return {"success": False, "error": str(exc)}


def get_saved_research_support(
    recommendation_id: int,
    user_id: Optional[int] = None,
) -> dict[str, Any]:
    try:
        return _get_service().get_research_output(recommendation_id, user_id)
    except Exception as exc:
        log.exception(
            "get_saved_research_support failed recommendation_id=%s user_id=%s",
            recommendation_id,
            user_id,
        )
        return {"success": False, "error": str(exc)}


def delete_saved_research_support(
    recommendation_id: int,
    user_id: Optional[int] = None,
) -> dict[str, Any]:
    try:
        return _get_service().delete_research_output(recommendation_id, user_id)
    except Exception as exc:
        log.exception(
            "delete_saved_research_support failed recommendation_id=%s user_id=%s",
            recommendation_id,
            user_id,
        )
        return {"success": False, "error": str(exc)}
