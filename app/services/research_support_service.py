"""Business logic for research support assistant (Phase 1 dummy mode)."""

from __future__ import annotations

import json
import os
from typing import Any, Optional
from urllib.parse import quote_plus
import re

from app.config.ai_config import get_ai_config
from app.repositories.research_output_repository import ResearchOutputRepository
from app.schemas.research_support_schema import (
    get_research_type_template,
    get_supported_research_types,
    validate_research_inputs,
)
from app.services.ollama_service import OllamaService
from app.utils.logger import get_logger

log = get_logger(__name__)

DEBUG_RESEARCH_OUTPUT = os.getenv("STACKWISE_DEBUG_RESEARCH", "0").strip().lower() in {"1", "true", "yes", "on"}

SCOPUS_VERIFICATION_NOTE = (
    "Scopus indexing must be manually verified through official Scopus sources or the "
    "journal/conference website. StackWise AI does not automatically claim that any "
    "venue is Scopus-indexed."
)

ACADEMIC_SAFETY_NOTES = [
    "AI-generated research content is only a draft.",
    "Users must review, edit, and validate the content.",
    "Suggested journals and publication venues must be manually verified.",
    "Related studies must be searched and cited from real sources.",
    "The system must not invent verified citations.",
    "Scopus indexing must be manually verified.",
]


class ResearchSupportService:
    def __init__(self, repository: ResearchOutputRepository) -> None:
        self._repository = repository
        self._ollama = OllamaService(get_ai_config())

    def check_ollama_available(self) -> dict[str, Any]:
        return self._ollama.check_ollama_available()

    def get_supported_research_types(self) -> dict[str, Any]:
        return {"success": True, "data": get_supported_research_types()}

    def get_research_type_template(self, research_type: str) -> dict[str, Any]:
        template = get_research_type_template(research_type)
        if not template:
            return {"success": False, "error": f"Unsupported research type: {research_type}"}
        return {"success": True, "data": template}

    def validate_research_request(self, research_type: str, research_inputs: dict[str, Any]) -> dict[str, Any]:
        result = validate_research_inputs(research_type, research_inputs)
        if not result.get("success") and "error" in result:
            return {"success": False, "error": result["error"], "missing_fields": []}
        return result

    def prepare_research_context(
        self,
        recommendation_data: dict[str, Any],
        project_data: dict[str, Any],
        research_type: str,
        research_inputs: dict[str, Any],
    ) -> dict[str, Any]:
        project_name = str(
            project_data.get("project_name")
            or recommendation_data.get("project_name")
            or "Untitled Project"
        ).strip()
        project_type = str(
            project_data.get("project_type")
            or recommendation_data.get("project_type")
            or "Software Project"
        ).strip()
        project_goal = str(
            project_data.get("project_goal")
            or recommendation_data.get("project_goal")
            or "Build a useful IT system"
        ).strip()
        selected_features = self._normalize_features(
            project_data.get("selected_features")
            or recommendation_data.get("selected_features")
            or []
        )
        research_title = str(research_inputs.get("research_title") or "").strip()
        merged = {
            "project_name": project_name,
            "project_type": project_type,
            "project_goal": project_goal,
            "selected_features": selected_features,
            "recommended_language": str(recommendation_data.get("recommended_language") or "N/A"),
            "recommended_framework": str(recommendation_data.get("recommended_framework") or "N/A"),
            "recommended_sdlc": str(recommendation_data.get("recommended_sdlc") or "N/A"),
            "confidence_score": recommendation_data.get("confidence_score"),
            "research_type": research_type,
            "research_title": research_title or project_name,
            "research_inputs": research_inputs or {},
        }
        return {"success": True, "data": merged}

    def build_dummy_research_output(
        self,
        recommendation_data: dict[str, Any],
        project_data: dict[str, Any],
        research_type: str,
        research_inputs: dict[str, Any],
    ) -> dict[str, Any]:
        validation = self.validate_research_request(research_type, research_inputs)
        if not validation.get("success"):
            return {
                "success": False,
                "error": validation.get("error") or "Missing required fields.",
                "missing_fields": validation.get("missing_fields", []),
            }

        template_result = self.get_research_type_template(research_type)
        if not template_result.get("success"):
            return template_result

        context_result = self.prepare_research_context(
            recommendation_data,
            project_data,
            research_type,
            research_inputs,
        )
        context = context_result["data"]
        template = template_result["data"]

        research_title = str(research_inputs.get("research_title") or context["project_name"])

        research_draft = {
            section: self._build_section_placeholder(section, context, research_title)
            for section in template["output_sections"]
        }
        if "recommendations" in research_draft:
            research_draft["recommendations"] += "\n\nAcademic Safety Notes:\n- " + "\n- ".join(ACADEMIC_SAFETY_NOTES)

        search_queries = self._build_search_queries(context)
        open_access_links = self._build_open_access_links(search_queries)

        output = {
            "research_type": research_type,
            "research_title": research_title,
            "research_inputs": research_inputs,
            "research_draft": research_draft,
            "suggested_journals": self._build_dummy_venues(research_type),
            "search_queries": search_queries,
            "open_access_links": open_access_links,
            "publication_recommendation": self._build_publication_recommendation(
                recommendation_data,
                project_data,
                research_type,
            ),
            "scopus_verification_note": SCOPUS_VERIFICATION_NOTE,
            "generated_by_model": "dummy-local-template",
        }
        return {"success": True, "data": output}

    def save_research_output(
        self,
        recommendation_id: int,
        user_id: Optional[int],
        research_output_data: dict[str, Any],
    ) -> dict[str, Any]:
        return self._repository.save_or_update_research_output(
            recommendation_id,
            user_id,
            research_output_data,
        )

    def get_research_output(
        self,
        recommendation_id: int,
        user_id: Optional[int] = None,
    ) -> dict[str, Any]:
        return self._repository.get_by_recommendation_id(recommendation_id, user_id)

    def has_research_output(
        self,
        recommendation_id: int,
        user_id: Optional[int] = None,
    ) -> dict[str, Any]:
        return self._repository.has_research_output(recommendation_id, user_id)

    def delete_research_output(
        self,
        recommendation_id: int,
        user_id: Optional[int] = None,
    ) -> dict[str, Any]:
        return self._repository.delete_by_recommendation_id(recommendation_id, user_id)

    def generate_ai_research_support(
        self,
        recommendation_id: Optional[int],
        recommendation_data: dict[str, Any],
        project_data: dict[str, Any],
        research_type: str,
        research_inputs: dict[str, Any],
    ) -> dict[str, Any]:
        context_result = self.prepare_research_context(
            recommendation_data,
            project_data,
            research_type,
            research_inputs,
        )
        if not context_result.get("success"):
            return context_result

        context = context_result["data"]
        context["recommendation_id"] = recommendation_id
        context["original_research_title"] = str(research_inputs.get("research_title") or "").strip()
        config = self._ollama.config
        log.info(
            "Research Ollama config: base_url=%s model=%s",
            config.base_url,
            config.model,
        )
        prompt = self.build_research_generation_prompt(
            recommendation_data,
            project_data,
            research_type,
            research_inputs,
        )
        model_label = self._ollama_model_label()
        self._log_research_generation_start(context, research_type, model_label)

        health = self._ollama.check_ollama_available()
        log.info(
            "Research Ollama health check: ollama_available=%s model_found=%s",
            bool(health.get("success")),
            bool(health.get("model_found")),
        )
        if not health.get("success"):
            return {
                "success": False,
                "error": str(health.get("error") or "Ollama is not running or unreachable."),
                "error_type": str(health.get("error_type") or "unreachable"),
                "models": health.get("models") or [],
                "model_found": bool(health.get("model_found")),
            }

        raw = self._ollama.generate(prompt, prefer_json_format=True)
        if not raw.get("success"):
            error_type = str(raw.get("error_type") or "request_error")
            return {
                "success": False,
                "error": str(raw.get("error") or "Research generation failed."),
                "error_type": error_type,
                "status_code": raw.get("status_code"),
            }

        response_text = str(raw.get("response_text") or "")
        parsed = self.parse_ollama_research_response(response_text)
        self._log_research_generation_response(raw, parsed, model_label)
        if not parsed.get("success"):
            return {
                "success": False,
                "error": "Ollama responded, but the response was not in the required JSON format. Please regenerate.",
                "error_type": "invalid_json",
                "status_code": raw.get("status_code"),
                "raw_response": raw.get("response_text"),
            }

        parsed_output = parsed.get("data") or {}
        repaired = self.repair_research_output_if_needed(
            parsed_output,
            research_type,
            {
                "recommendation_data": recommendation_data,
                "project_data": project_data,
                "research_inputs": research_inputs,
                "context": context,
                "model_label": model_label,
            },
        )
        if not repaired.get("success"):
            return repaired

        repaired_data = repaired["data"]
        repaired_data["generated_by_model"] = model_label
        repaired_data = self._sanitize_generated_output(repaired_data, research_type, context)
        validation = self.validate_research_output_structure(repaired_data, research_type)
        if not validation.get("success"):
            return {
                "success": False,
                "error": "Ollama responded, but the response was not in the required JSON format. Please regenerate.",
                "error_type": "invalid_json",
                "validation_error": validation.get("error"),
                "missing_sections": validation.get("missing_sections", []),
            }

        repaired_data["generated_by_model"] = model_label
        self._log_research_generation_completion(repaired_data, model_label)
        return {"success": True, "data": repaired_data, "generated_by_model": model_label}

    def build_research_generation_prompt(
        self,
        recommendation_data: dict[str, Any],
        project_data: dict[str, Any],
        research_type: str,
        research_inputs: dict[str, Any],
    ) -> str:
        template = get_research_type_template(research_type) or {}
        sections = [str(section).strip() for section in template.get("output_sections") or [] if str(section).strip()]
        original_title = str(
            research_inputs.get("research_title")
            or project_data.get("project_name")
            or recommendation_data.get("project_name")
            or "Untitled Research"
        ).strip()
        improved_title = self._derive_improved_research_title(
            research_type,
            recommendation_data,
            project_data,
            research_inputs,
        )

        payload = {
            "recommendation_data": recommendation_data,
            "project_data": project_data,
            "research_type": research_type,
            "research_inputs": research_inputs,
            "required_sections": sections,
            "original_research_title": original_title,
            "improved_research_title": improved_title,
        }

        return (
            "You are StackWise AI, an academic research writing assistant for software projects.\n"
            "Return valid JSON only. Do not wrap the response in markdown.\n"
            "Do not use ```json fences.\n"
            "Do not include explanations, comments, prefixes, suffixes, or any non-JSON text.\n"
            "Do not omit required keys.\n"
            "Do not invent verified citations, journal indexing claims, DOIs, volume numbers, issue numbers, or page ranges.\n"
            "If a fact cannot be verified from the provided context, describe it cautiously and add a verification note instead of making it up.\n"
            "All sections must contain real academic prose written as a draft suitable for academic review.\n"
            "Do not write placeholder phrases such as 'This section will discuss', 'Draft for', 'Insert', 'To be completed', or 'This section requires further completion'.\n"
            "Avoid raw JSON arrays or Python-style lists inside section bodies. When a section needs multiple items, write them as numbered lines inside the string.\n"
            "Use formal academic tone, balanced depth, and paragraph structure. The draft should feel complete but not exaggerated.\n\n"
            f"Research type: {research_type}\n"
            f"Original user title: {original_title}\n"
            f"Improved academic title to use: {improved_title}\n"
            f"Required research_draft keys: {json.dumps(sections, ensure_ascii=False)}\n\n"
            "Writing targets:\n"
            "- Abstract: 150 to 220 words, single paragraph, includes context, purpose, system description, SDLC, technology stack, and significance.\n"
            "- Introduction: 3 to 5 paragraphs that explain the background, the decision-making problem, the project context, and why the selected stack matters.\n"
            "- Existing system or current process: 2 to 3 paragraphs describing the current workflow and limitations.\n"
            "- Proposed system: 2 to 3 paragraphs explaining the proposed solution, major features, target users, and expected improvement.\n"
            "- Statement of the problem: start with the main problem, then provide 1 general problem and 3 to 5 specific problems.\n"
            "- Objectives: provide 1 general objective and 3 to 5 specific objectives that clearly answer the specific problems.\n"
            "- Scope and limitations: 2 to 4 paragraphs or compact bullet-style lines describing scope, users, platform, features, and limitations.\n"
            "- Significance: write by beneficiary group with 2 to 4 sentences per group.\n"
            "- System architecture overview: explain high-level frontend, backend, database, and rule-based recommendation flow; mention Ollama only as a separate writing assistant if relevant.\n"
            "- Development methodology: explain the selected SDLC model, why it fits the project, and its phases.\n"
            "- Technology stack justification: justify the language, framework, and SDLC as a decision-support recommendation, not an absolute claim.\n"
            "- Testing and evaluation plan: include functional, usability, security, performance, and user acceptance testing where relevant.\n"
            "- Conclusion: 1 to 3 paragraphs summarizing expected contribution without claiming completed results.\n"
            "- Recommendations: 5 to 7 practical items focused on validation, usability, security, documentation, deployment, future features, and source verification.\n"
            "- Suggested references or search queries: do not invent final APA references. Provide search queries, citation placeholder topics, and a reminder that verified sources must replace placeholders.\n\n"
            "Important section-specific writing rules for System Development Research:\n"
            "- title_page: include the improved title, project/system name, research type, academic level, institution if provided, locale if provided, and target users.\n"
            "- abstract: write one coherent paragraph with all required elements.\n"
            "- statement_of_the_problem: use proper SOP format with one general problem and numbered specific problems.\n"
            "- objectives: use one general objective and numbered specific objectives.\n"
            "- suggested_references_or_search_queries: use safe search queries and citation placeholder topics only.\n"
            "- Do not generate fake authors, fake article titles, fake journal names, fake DOI, fake volume/issue/page numbers, or fake Scopus claims.\n"
            "- If you need to mention literature support, use placeholders such as (Author, Year) or [Insert verified source about decision-support systems].\n\n"
            "Output JSON structure:\n"
            '{"improved_research_title":"...","research_draft":{"title_page":"...","abstract":"...","introduction":"..."}}\n\n'
            "The research_draft object must include every required section key from the selected template, with substantive academic content for each one.\n\n"
            "Context JSON:\n"
            f"{json.dumps(payload, ensure_ascii=False)}"
        )

    def parse_ollama_research_response(self, response_text: str) -> dict[str, Any]:
        text = str(response_text or "").strip()
        if not text:
            return {"success": False, "error": "Empty response from Ollama."}

        cleaned = self._clean_json_text(text)
        parsed = self._try_parse_json(cleaned)
        if parsed is not None:
            return {"success": True, "data": parsed, "parsed_via": "direct"}

        extracted = self._extract_json_candidate(cleaned)
        if extracted:
            parsed = self._try_parse_json(extracted)
            if parsed is not None:
                return {"success": True, "data": parsed, "parsed_via": "substring"}

        return {"success": False, "error": "Unable to parse JSON from Ollama response."}

    def validate_research_output_structure(self, output: dict[str, Any], research_type: str) -> dict[str, Any]:
        template = get_research_type_template(research_type)
        if not template:
            return {"success": False, "error": f"Unsupported research type: {research_type}"}

        required_sections = [str(x).strip() for x in template.get("output_sections") or [] if str(x).strip()]
        draft = output.get("research_draft")
        if not isinstance(draft, dict):
            return {"success": False, "error": "research_draft must be a dictionary.", "missing_sections": required_sections}

        missing = [section for section in required_sections if not str(draft.get(section) or "").strip()]
        missing_ratio = len(missing) / max(len(required_sections), 1)

        if not isinstance(output.get("suggested_journals"), list):
            return {"success": False, "error": "suggested_journals must be a list."}
        if not isinstance(output.get("search_queries"), list):
            return {"success": False, "error": "search_queries must be a list."}
        if not isinstance(output.get("open_access_links"), list):
            return {"success": False, "error": "open_access_links must be a list."}
        if not isinstance(output.get("publication_recommendation"), dict):
            return {"success": False, "error": "publication_recommendation must be a dictionary."}
        if "scopus_verification_note" not in output:
            return {"success": False, "error": "scopus_verification_note is missing."}

        if missing_ratio > 0.4:
            return {
                "success": False,
                "error": "The AI response could not be parsed into the required research format. Please regenerate.",
                "missing_sections": missing,
            }

        return {"success": True, "missing_sections": missing, "missing_ratio": missing_ratio}

    def repair_research_output_if_needed(
        self,
        output: dict[str, Any],
        research_type: str,
        context: dict[str, Any],
    ) -> dict[str, Any]:
        template = get_research_type_template(research_type) or {}
        required_sections = [str(section).strip() for section in template.get("output_sections") or [] if str(section).strip()]
        recommendation_data = context.get("recommendation_data") or {}
        project_data = context.get("project_data") or {}
        research_inputs = context.get("research_inputs") or {}
        context_data = context.get("context") or {}
        model_label = str(context.get("model_label") or self._ollama_model_label())

        normalized = dict(output or {})
        original_title = str(
            context.get("original_research_title")
            or research_inputs.get("research_title")
            or project_data.get("project_name")
            or recommendation_data.get("project_name")
            or "Untitled Research"
        ).strip()
        improved_title = self._normalize_title_text(
            normalized.get("improved_research_title")
            or normalized.get("research_title")
            or self._derive_improved_research_title(research_type, recommendation_data, project_data, research_inputs),
            fallback=original_title,
        )
        normalized["research_type"] = research_type
        normalized["original_research_title"] = original_title
        normalized["improved_research_title"] = improved_title
        normalized["research_title"] = original_title
        normalized["research_inputs"] = research_inputs
        normalized["generated_by_model"] = model_label

        draft = normalized.get("research_draft")
        if not isinstance(draft, dict):
            draft = {}

        missing = [section for section in required_sections if not str(draft.get(section) or "").strip()]
        if len(missing) / max(len(required_sections), 1) > 0.4:
            return {
                "success": False,
                "error": "The AI response could not be parsed into the required research format. Please regenerate.",
                "missing_sections": missing,
            }

        for section in missing:
            draft[section] = self._build_manual_completion_note(section, context_data, research_type)

        if "suggested_references_or_search_queries" in draft:
            draft["suggested_references_or_search_queries"] = self._build_reference_safety_section(
                research_type,
                context_data,
                research_inputs,
            )

        normalized["research_draft"] = {
            key: self._sanitize_research_text(value, section_key=key, research_type=research_type)
            for key, value in draft.items()
            if str(key).strip()
        }

        journals = normalized.get("suggested_journals")
        if not isinstance(journals, list) or not journals:
            normalized["suggested_journals"] = self._build_ai_venue_placeholders(research_type, context_data)
        else:
            normalized["suggested_journals"] = [self._sanitize_venue_item(item) for item in journals if isinstance(item, dict)]

        queries = normalized.get("search_queries")
        if not isinstance(queries, list) or not queries:
            normalized["search_queries"] = self._build_search_queries(context_data or self.prepare_research_context(recommendation_data, project_data, research_type, research_inputs)["data"])
        else:
            normalized["search_queries"] = [self._sanitize_query_item(item) for item in queries if isinstance(item, dict)]

        links = normalized.get("open_access_links")
        if not isinstance(links, list) or not links:
            normalized["open_access_links"] = self._build_open_access_links(normalized.get("search_queries") or [])
        else:
            normalized["open_access_links"] = [self._sanitize_link_item(item) for item in links if isinstance(item, dict)]

        publication = normalized.get("publication_recommendation")
        if not isinstance(publication, dict):
            publication = {}
        normalized["publication_recommendation"] = self._sanitize_publication_recommendation(
            publication,
            research_type,
            recommendation_data,
            project_data,
        )

        normalized["scopus_verification_note"] = SCOPUS_VERIFICATION_NOTE
        normalized["academic_safety_note"] = (
            "AI-generated content is a draft and requires human review, adviser validation, source verification, and editing before submission."
        )

        validation = self.validate_research_output_structure(normalized, research_type)
        if not validation.get("success"):
            return {
                "success": False,
                "error": validation.get("error") or "The AI response could not be parsed into the required research format. Please regenerate.",
                "missing_sections": validation.get("missing_sections", []),
            }

        return {"success": True, "data": normalized}

    def _build_manual_completion_note(self, section: str, context: dict[str, Any], research_type: str) -> str:
        project_name = str(context.get("project_name") or "the project")
        project_type = str(context.get("project_type") or "software project")
        research_title = str(context.get("research_title") or project_name)
        return (
            f"This section requires manual completion and adviser validation. "
            f"Rewrite it as a formal academic discussion for {research_type} titled '{research_title}' "
            f"within the context of {project_name}, a {project_type}."
        )

    def _build_reference_safety_section(
        self,
        research_type: str,
        context: dict[str, Any],
        research_inputs: dict[str, Any],
    ) -> str:
        search_queries = self._build_search_queries(context)
        placeholder_topics = [
            f"(Author, Year) decision support systems for {research_type.lower()}",
            f"(Author, Year) software technology stack recommendation methods",
            f"(Author, Year) SDLC selection for software project development",
            f"(Author, Year) user-centered evaluation of academic decision-support systems",
            f"(Author, Year) {str(research_inputs.get('research_title') or context.get('project_name') or 'the project')} implementation study",
        ]
        query_lines = [f"{idx + 1}. {item.get('query')}" for idx, item in enumerate(search_queries[:8]) if item.get("query")]
        topic_lines = [f"{idx + 1}. {topic}" for idx, topic in enumerate(placeholder_topics)]
        lines = [
            "Suggested Search Queries:",
            *query_lines,
            "",
            "Citation Placeholder Topics:",
            *topic_lines,
            "",
            "References must be replaced with verified sources retrieved from Google Scholar, DOAJ, Crossref, OpenAlex, Semantic Scholar, CORE, or institutional databases.",
        ]
        return "\n".join(line for line in lines if line is not None)

    def _derive_improved_research_title(
        self,
        research_type: str,
        recommendation_data: dict[str, Any],
        project_data: dict[str, Any],
        research_inputs: dict[str, Any],
    ) -> str:
        raw_title = str(
            research_inputs.get("research_title")
            or project_data.get("project_name")
            or recommendation_data.get("project_name")
            or "Untitled Research"
        ).strip()
        project_name = self._clean_title_phrase(raw_title)
        target_users = str(research_inputs.get("target_users") or project_data.get("target_users") or "software users").strip()
        project_goal = str(project_data.get("project_goal") or recommendation_data.get("project_goal") or "decision support for technology stack recommendation").strip()

        focus_map = {
            "System Development Research": "Decision-Support System",
            "Feasibility Study": "Feasibility Study",
            "AI / Machine Learning Research Proposal": "AI/ML Research Proposal",
            "Capstone Project Proposal": "Capstone Project Proposal",
            "Software Requirements and Design Study": "Requirements and Design Study",
            "Comparative Technology Evaluation": "Comparative Technology Evaluation",
            "Action Research for IT Solution": "Action Research Study",
        }
        focus = focus_map.get(research_type, "Academic Study")

        if project_name.lower().startswith("development of "):
            base = project_name
        else:
            base = f"Development of {project_name}"

        title = f"{base}: A {focus} for {target_users or project_goal}".strip()
        title = re.sub(r"\s+", " ", title)
        return self._normalize_title_text(title, fallback=raw_title)

    def _clean_title_phrase(self, title: str) -> str:
        text = str(title or "").strip()
        text = re.sub(r"\s+", " ", text)
        text = text.strip("-:;,. ")
        if not text:
            return "Untitled Research"
        return text

    def _normalize_title_text(self, title: Any, *, fallback: str) -> str:
        text = self._clean_title_phrase(str(title or ""))
        if not text or text.lower() in {"untitled", "untitled research", "research title"}:
            return self._clean_title_phrase(fallback)
        return text

    def _sanitize_generated_output(
        self,
        output: dict[str, Any],
        research_type: str,
        context: dict[str, Any],
    ) -> dict[str, Any]:
        normalized = dict(output or {})
        draft = normalized.get("research_draft") if isinstance(normalized.get("research_draft"), dict) else {}
        normalized["research_draft"] = {
            str(key): self._sanitize_research_text(value, section_key=str(key), research_type=research_type)
            for key, value in draft.items()
        }

        journals = normalized.get("suggested_journals") if isinstance(normalized.get("suggested_journals"), list) else []
        normalized["suggested_journals"] = [self._sanitize_venue_item(item) for item in journals if isinstance(item, dict)]

        queries = normalized.get("search_queries") if isinstance(normalized.get("search_queries"), list) else []
        normalized["search_queries"] = [self._sanitize_query_item(item) for item in queries if isinstance(item, dict)]

        links = normalized.get("open_access_links") if isinstance(normalized.get("open_access_links"), list) else []
        normalized["open_access_links"] = [self._sanitize_link_item(item) for item in links if isinstance(item, dict)]

        publication = normalized.get("publication_recommendation") if isinstance(normalized.get("publication_recommendation"), dict) else {}
        normalized["publication_recommendation"] = self._sanitize_publication_recommendation(
            publication,
            research_type,
            context.get("recommendation_data") or {},
            context.get("project_data") or {},
        )

        if not str(normalized.get("generated_by_model") or "").strip():
            normalized["generated_by_model"] = self._ollama_model_label()

        normalized["scopus_verification_note"] = SCOPUS_VERIFICATION_NOTE
        normalized["academic_safety_note"] = (
            "AI-generated content is a draft and requires human review, adviser validation, source verification, and editing before submission."
        )
        return normalized

    def _sanitize_research_text(self, text: Any, *, section_key: str, research_type: str) -> str:
        _ = section_key, research_type
        raw = self._format_research_text_value(text).strip()
        if not raw:
            return ""
        raw = re.sub(r"\bScopus-indexed\b", "Indexing status must be manually verified", raw, flags=re.IGNORECASE)
        raw = re.sub(r"\bWeb of Science indexed\b", "Indexing status must be manually verified", raw, flags=re.IGNORECASE)
        raw = re.sub(r"\bCHED-recognized\b", "Official recognition must be manually verified", raw, flags=re.IGNORECASE)
        raw = re.sub(r"\bdoi:\s*[A-Za-z0-9./_-]+\b", "DOI must be manually verified", raw, flags=re.IGNORECASE)
        raw = re.sub(r"\bvol\.?\s*\d+\b", "Volume must be manually verified", raw, flags=re.IGNORECASE)
        raw = re.sub(r"\bissue\s*\d+\b", "Issue must be manually verified", raw, flags=re.IGNORECASE)
        raw = re.sub(r"\bpp\.?\s*\d+(?:[-–]\d+)?\b", "Page range must be manually verified", raw, flags=re.IGNORECASE)
        return raw.strip()

    def _format_research_text_value(self, value: Any) -> str:
        if value is None:
            return ""
        if isinstance(value, str):
            return value.strip()
        if isinstance(value, list):
            lines: list[str] = []
            for index, item in enumerate(value, start=1):
                item_text = self._format_research_text_value(item)
                if item_text:
                    lines.append(f"{index}. {item_text}")
            return "\n".join(lines).strip()
        if isinstance(value, dict):
            lines: list[str] = []
            for key, item in value.items():
                label = str(key).replace("_", " ").strip().title()
                item_text = self._format_research_text_value(item)
                if not item_text:
                    continue
                if "\n" in item_text:
                    block = "\n".join(f"  {line}" for line in item_text.splitlines())
                    lines.append(f"{label}:\n{block}")
                else:
                    lines.append(f"{label}: {item_text}")
            return "\n".join(lines).strip()
        return str(value).strip()

    def _sanitize_query_item(self, item: dict[str, Any]) -> dict[str, str]:
        return {
            "query": str(item.get("query") or "").strip(),
            "purpose": str(item.get("purpose") or "").strip(),
        }

    def _sanitize_link_item(self, item: dict[str, Any]) -> dict[str, str]:
        return {
            "source_name": str(item.get("source_name") or "").strip(),
            "search_url": str(item.get("search_url") or "").strip(),
            "purpose": str(item.get("purpose") or "").strip(),
        }

    def _build_ai_venue_placeholders(self, research_type: str, context: dict[str, Any]) -> list[dict[str, str]]:
        _ = context
        return [
            {
                "venue_name": "Suggested Academic Venue 1",
                "venue_type": "Journal or Conference",
                "field_relevance": f"Relevant to {research_type}",
                "why_suggested": "Verify relevance, peer-review requirements, and indexing manually before submission.",
                "verification_note": "Indexing status must be manually verified.",
            },
            {
                "venue_name": "Suggested Academic Venue 2",
                "venue_type": "Journal or Conference",
                "field_relevance": f"Relevant to {research_type}",
                "why_suggested": "Use as a search lead only, not as a verified publication claim.",
                "verification_note": "Indexing status must be manually verified.",
            },
        ]

    def _sanitize_venue_item(self, item: dict[str, Any]) -> dict[str, str]:
        out = {
            "venue_name": str(item.get("venue_name") or "").strip(),
            "venue_type": str(item.get("venue_type") or "").strip(),
            "field_relevance": str(item.get("field_relevance") or "").strip(),
            "why_suggested": str(item.get("why_suggested") or "").strip(),
            "verification_note": str(item.get("verification_note") or "").strip() or "Indexing status must be manually verified.",
        }
        if not out["verification_note"]:
            out["verification_note"] = "Indexing status must be manually verified."
        out["venue_name"] = self._sanitize_research_text(out["venue_name"], section_key="venue_name", research_type="")
        out["why_suggested"] = self._sanitize_research_text(out["why_suggested"], section_key="why_suggested", research_type="")
        return out

    def _sanitize_publication_recommendation(
        self,
        publication: dict[str, Any],
        research_type: str,
        recommendation_data: dict[str, Any],
        project_data: dict[str, Any],
    ) -> dict[str, Any]:
        normalized = self._build_publication_recommendation(recommendation_data, project_data, research_type)
        merged = dict(normalized)
        merged.update({k: str(v or "").strip() for k, v in publication.items() if k in {"recommended_level", "reason", "improvement_needed"}})
        reason = self._sanitize_research_text(merged.get("reason"), section_key="publication_reason", research_type=research_type)
        improvement = self._sanitize_research_text(merged.get("improvement_needed"), section_key="publication_improvement", research_type=research_type)
        if "scopus" in reason.lower():
            reason = "Indexing status must be manually verified."
        if "scopus" in improvement.lower():
            improvement = "Indexing status must be manually verified."
        return {
            "recommended_level": str(merged.get("recommended_level") or "Capstone project").strip(),
            "reason": reason or "This research output requires manual validation before publication claims are made.",
            "improvement_needed": improvement or "Add validation, testing evidence, and verified related literature before submission.",
        }

    def _clean_json_text(self, text: str) -> str:
        raw = str(text or "").strip()
        if raw.startswith("```json"):
            raw = raw.removeprefix("```json").strip()
        if raw.startswith("```"):
            raw = raw.removeprefix("```").strip()
        if raw.endswith("```"):
            raw = raw[:-3].strip()
        raw = raw.replace("\r\n", "\n")
        return raw

    def _extract_json_candidate(self, text: str) -> str:
        start = text.find("{")
        end = text.rfind("}")
        if start >= 0 and end > start:
            return text[start : end + 1]
        return ""

    def _try_parse_json(self, text: str) -> dict[str, Any] | None:
        if not text:
            return None
        try:
            parsed = json.loads(text)
        except Exception:
            return None
        return parsed if isinstance(parsed, dict) else None

    def _ollama_model_label(self) -> str:
        model = str(get_ai_config().model or "llama3.2").strip() or "llama3.2"
        if model.startswith("ollama:"):
            return model
        return f"ollama:{model}"

    def _debug_preview(self, text: str) -> str:
        preview = str(text or "")[:300]
        return preview.replace("\n", "\\n")

    def _log_research_generation_start(self, context: dict[str, Any], research_type: str, model_label: str) -> None:
        log.info(
            "Research AI generation started: recommendation_id=%s research_type=%s research_title=%s project_name=%s ollama_base_url=%s ollama_model=%s",
            context.get("recommendation_id"),
            research_type,
            context.get("research_title"),
            context.get("project_name"),
            self._ollama.config.base_url,
            self._ollama.config.model,
        )

    def _log_research_generation_response(self, raw: dict[str, Any], parsed: dict[str, Any], model_label: str) -> None:
        response_text = str(raw.get("response_text") or "")
        missing_sections = 0
        parsed_data = parsed.get("data") if isinstance(parsed, dict) else {}
        draft = parsed_data.get("research_draft") if isinstance(parsed_data, dict) else {}
        if isinstance(draft, dict):
            template = get_research_type_template(str(parsed_data.get("research_type") or "")) or {}
            required = [str(section).strip() for section in template.get("output_sections") or [] if str(section).strip()]
            missing_sections = len([section for section in required if not str(draft.get(section) or "").strip()])

        log.info(
            "Research AI response received: status_code=%s response_length=%s response_preview=%s parse_success=%s missing_sections_count=%s generated_by_model=%s",
            raw.get("status_code"),
            len(response_text),
            self._debug_preview(response_text),
            bool(parsed.get("success")),
            missing_sections,
            model_label,
        )

    def _log_research_generation_completion(self, output: dict[str, Any], model_label: str) -> None:
        draft = output.get("research_draft") if isinstance(output, dict) else {}
        section_count = len(draft) if isinstance(draft, dict) else 0
        log.info(
            "Research AI generation completed: generated_by_model=%s section_count=%s",
            model_label,
            section_count,
        )

    def _build_section_placeholder(self, section: str, context: dict[str, Any], research_title: str) -> str:
        project_name = str(context.get("project_name") or "this project")
        project_type = str(context.get("project_type") or "software project")
        research_type = str(context.get("research_type") or "research paper")
        recommended_language = str(context.get("recommended_language") or "N/A")
        recommended_framework = str(context.get("recommended_framework") or "N/A")
        recommended_sdlc = str(context.get("recommended_sdlc") or "N/A")
        project_goal = str(context.get("project_goal") or "")
        features = self._normalize_features(context.get("selected_features") or [])
        feature_text = ", ".join(features[:5]) if features else "core application modules"

        section_key = str(section or "").strip()
        section_label = section_key.replace("_", " ").title()

        specific_templates = {
            "title_page": (
                f"Title page for the academic paper titled '{research_title}' about {project_name}. "
                f"The paper supports a {research_type} on {project_type} development."
            ),
            "abstract": (
                f"This abstract will summarize the problem, proposed system, methodology, expected output, and evaluation plan for '{research_title}'."
            ),
            "introduction": (
                f"This introduction will present the research context, the current project '{project_name}', and the academic purpose of '{research_title}'."
            ),
            "background_of_the_study": (
                f"This section will explain the background behind {project_name}, the project goal, and the reason the study is needed."
            ),
            "statement_of_the_problem": (
                f"This section will identify the specific problems addressed by '{research_title}' for {project_name}."
            ),
            "objectives_of_the_study": (
                f"This section will outline the general and specific objectives for the study of {project_name}."
            ),
            "scope_and_limitations": (
                f"This section will define the scope, limitations, and boundaries of the research for {project_name}."
            ),
            "significance_of_the_study": (
                f"This section will explain who benefits from the proposed solution for {project_name} and why the study matters."
            ),
            "proposed_system_overview": (
                f"This section will introduce the proposed system for {project_name} and its major capabilities."
            ),
            "methodology": (
                f"This section will describe the research and development methodology used for '{research_title}'."
            ),
            "system_development_model": (
                f"This section will justify the use of the {recommended_sdlc} model for the development of {project_name}."
            ),
            "recommended_technology_stack": (
                f"This section will justify the selected language, framework, and stack for {project_name}: {recommended_language} + {recommended_framework}."
            ),
            "expected_output": (
                f"This section will describe the expected deliverables and system outputs for {project_name}."
            ),
            "conclusion": (
                f"This section will conclude the study and restate the value of '{research_title}'."
            ),
            "recommendations": (
                f"This section will provide research and implementation recommendations for {project_name}."
            ),
            "suggested_references_or_search_queries": (
                f"This section will list search directions and related literature queries for '{research_title}'."
            ),
            "existing_system_or_current_process": (
                "This section will describe the current process and limitations identified by the researcher."
            ),
            "proposed_system": (
                f"This section will explain how the proposed system addresses the identified problems in {project_name}."
            ),
            "technology_stack_justification": (
                f"This section will justify why {recommended_language} and {recommended_framework} were selected for {project_name}."
            ),
            "testing_and_evaluation_plan": (
                f"This section will describe planned functional testing, user evaluation, and validation activities for {project_name}."
            ),
            "project_overview": (
                f"This section will summarize {project_name}, its goal, and the context of the project."
            ),
            "stakeholder_analysis": (
                f"This section will identify the stakeholders and their roles in {project_name}."
            ),
            "functional_requirements": (
                f"This section will list the functional requirements for {project_name}."
            ),
            "non_functional_requirements": (
                f"This section will define the non-functional requirements for {project_name}."
            ),
            "use_case_overview": (
                f"This section will outline the major use cases for {project_name}."
            ),
            "data_requirements": (
                f"This section will describe the data requirements needed for {project_name}."
            ),
            "system_design_overview": (
                f"This section will describe the architecture and design approach for {project_name}."
            ),
            "sdlc_justification": (
                f"This section will justify the chosen {recommended_sdlc} approach for {project_name}."
            ),
            "risk_and_constraint_analysis": (
                f"This section will discuss risks and constraints affecting {project_name}."
            ),
            "executive_summary": (
                f"This section will summarize the feasibility of {project_name} and the findings of the study."
            ),
            "project_description": (
                f"This section will describe the project concept, goals, and intended solution for {project_name}."
            ),
            "technical_feasibility": (
                f"This section will assess whether {project_name} can be built with the available technology stack and resources."
            ),
            "operational_feasibility": (
                f"This section will evaluate whether users and stakeholders can realistically use {project_name}."
            ),
            "economic_feasibility": (
                f"This section will assess costs and resource implications for {project_name}."
            ),
            "schedule_feasibility": (
                f"This section will assess whether {project_name} can be delivered within the estimated timeline."
            ),
            "risk_analysis": (
                f"This section will identify risks, constraints, and mitigation options for {project_name}."
            ),
            "implementation_considerations": (
                f"This section will describe implementation factors that may affect {project_name}."
            ),
            "dataset_description": (
                f"This section will describe the dataset source and structure for '{research_title}'."
            ),
            "proposed_ai_or_ml_approach": (
                f"This section will explain the AI/ML approach only if '{research_title}' truly requires it."
            ),
            "model_development_methodology": (
                f"This section will describe model development, training, and validation methods for '{research_title}'."
            ),
            "evaluation_metrics": (
                f"This section will define the metrics used to evaluate the proposed approach for '{research_title}'."
            ),
            "ethical_considerations": (
                f"This section will describe ethical, privacy, and data handling concerns for '{research_title}'."
            ),
            "expected_results": (
                f"This section will describe the expected research outcomes for '{research_title}'."
            ),
            "evaluation_problem": (
                f"This section will define the comparison problem and the reason for evaluating technologies in {project_name}."
            ),
            "technology_candidates": (
                f"This section will list the candidate technologies being compared for {project_name}."
            ),
            "weighted_scoring_method": (
                f"This section will explain the weighted scoring method used to compare technologies for {project_name}."
            ),
            "comparison_results": (
                f"This section will present the comparison results for the candidate technologies in {project_name}."
            ),
            "discussion": (
                f"This section will discuss the comparison results and their implications for {project_name}."
            ),
            "problem_context": (
                f"This section will describe the problem context and why {project_name} is being studied."
            ),
            "action_research_objective": (
                f"This section will explain the objective of the action research for {project_name}."
            ),
            "participants_or_users": (
                f"This section will identify the participants or users involved in {project_name}."
            ),
            "intervention_or_proposed_system": (
                f"This section will describe the intervention or proposed system for {project_name}."
            ),
            "implementation_plan": (
                f"This section will outline the implementation plan for {project_name}."
            ),
            "data_collection_plan": (
                f"This section will describe how data will be collected during the action research for {project_name}."
            ),
            "evaluation_plan": (
                f"This section will describe how the intervention will be evaluated for {project_name}."
            ),
            "reflection_and_improvement_cycle": (
                f"This section will describe the reflection and improvement cycle for {project_name}."
            ),
        }

        if section_key in specific_templates:
            return specific_templates[section_key]

        return (
            f"This section is a placeholder draft for the {research_type} paper titled '{research_title}'. "
            f"It discusses the development of '{project_name}' as a {project_type} using {recommended_language} "
            f"and {recommended_framework}, guided by the {recommended_sdlc} model. Key scope signals: {feature_text}. "
            f"Project goal context: {project_goal or 'N/A'}."
        )

    def _normalize_features(self, features: Any) -> list[str]:
        if isinstance(features, str):
            items = re.split(r"[|,;]", features)
            return [item.strip() for item in items if item.strip()]
        if isinstance(features, (tuple, set)):
            return [str(item).strip() for item in features if str(item).strip()]
        if isinstance(features, list):
            return [str(item).strip() for item in features if str(item).strip()]
        return []

    def _build_search_queries(self, context: dict[str, Any]) -> list[dict[str, str]]:
        project_name = str(context.get("project_name") or "software project")
        project_type = str(context.get("project_type") or "software system")
        project_goal = str(context.get("project_goal") or "IT solution")
        features = context.get("selected_features") or []
        feat = " ".join(str(x) for x in features[:3]) if features else "system development"
        lang = str(context.get("recommended_language") or "")
        framework = str(context.get("recommended_framework") or "")
        sdlc = str(context.get("recommended_sdlc") or "")
        rtype = str(context.get("research_type") or "")

        return [
            {"query": f"{project_name} {project_type} {rtype}", "purpose": "Find research papers with similar project framing and paper type."},
            {"query": f"{project_goal} information technology capstone", "purpose": "Locate applied capstone and undergraduate studies with related goals."},
            {"query": f"{lang} {framework} {project_type} development study", "purpose": "Gather stack-specific implementation and evaluation references."},
            {"query": f"{sdlc} methodology {project_type} case study", "purpose": "Support methodology and process justification."},
            {"query": f"{feat} software requirements analysis", "purpose": "Find requirements and design evidence connected to selected features."},
            {"query": f"{project_name} system evaluation metrics", "purpose": "Identify testing/evaluation approaches for similar solutions."},
        ]

    def _build_open_access_links(self, queries: list[dict[str, str]]) -> list[dict[str, str]]:
        best_query = queries[0]["query"] if queries else "software project research"
        encoded = quote_plus(best_query)
        return [
            {
                "source_name": "Google Scholar",
                "search_url": f"https://scholar.google.com/scholar?q={encoded}",
                "purpose": "Find broad scholarly articles and citations.",
            },
            {
                "source_name": "DOAJ",
                "search_url": f"https://doaj.org/search/articles?ref=homepage-box&q={encoded}",
                "purpose": "Find open-access journal articles.",
            },
            {
                "source_name": "OpenAlex",
                "search_url": f"https://openalex.org/works?filter=default.search:{encoded}",
                "purpose": "Discover indexed works and metadata for related studies.",
            },
            {
                "source_name": "Crossref",
                "search_url": f"https://search.crossref.org/?q={encoded}",
                "purpose": "Locate DOI-backed scholarly records.",
            },
            {
                "source_name": "Semantic Scholar",
                "search_url": f"https://www.semanticscholar.org/search?q={encoded}",
                "purpose": "Find related papers, abstracts, and citation graph leads.",
            },
            {
                "source_name": "CORE",
                "search_url": f"https://core.ac.uk/search?q={encoded}",
                "purpose": "Search open research repositories and full-text resources.",
            },
        ]

    def _build_dummy_venues(self, research_type: str) -> list[dict[str, str]]:
        return [
            {
                "venue_name": "Local Undergraduate Research Conference",
                "venue_type": "Conference",
                "field_relevance": "Information Technology / Computer Science",
                "why_suggested": f"Suitable for applied system development and {research_type.lower()} outputs.",
                "verification_note": "Verify submission requirements and indexing status manually.",
            },
            {
                "venue_name": "Campus Journal of Computing Projects",
                "venue_type": "Institutional Journal",
                "field_relevance": "Software Engineering / Information Systems",
                "why_suggested": "Good fit for capstone-scale studies with practical evaluation.",
                "verification_note": "Confirm editorial policy, peer-review process, and indexing claims.",
            },
            {
                "venue_name": "Regional ICT Innovation Forum",
                "venue_type": "Symposium",
                "field_relevance": "Applied IT Solutions and Emerging Technologies",
                "why_suggested": "Appropriate for prototypes, feasibility findings, and comparative evaluations.",
                "verification_note": "Check venue legitimacy and publication pathways before submission.",
            },
        ]

    def _build_publication_recommendation(
        self,
        recommendation_data: dict[str, Any],
        project_data: dict[str, Any],
        research_type: str,
    ) -> dict[str, str]:
        text_blob = " ".join(
            [
                str(recommendation_data.get("project_type") or ""),
                str(project_data.get("project_goal") or recommendation_data.get("project_goal") or ""),
                str(project_data.get("complexity") or recommendation_data.get("complexity") or ""),
                str(project_data.get("selected_features") or recommendation_data.get("selected_features") or ""),
                research_type,
            ]
        ).lower()

        has_ai_signal = any(
            k in text_blob
            for k in [
                "ai",
                "machine learning",
                "prediction",
                "chatbot",
                "nlp",
                "data science",
                "machine-learning",
                "deep learning",
                "neural",
            ]
        )
        has_ai_related_project = any(
            k in text_blob
            for k in [
                "ai / machine learning research proposal",
                "artificial intelligence",
                "machine learning",
                "prediction",
                "chatbot",
                "nlp",
                "data science",
            ]
        )
        has_eval_signal = any(k in text_blob for k in ["evaluation", "experiment", "dataset", "validation", "metric"])
        is_prototype = any(k in text_blob for k in ["prototype", "proof of concept", "mvp"])
        is_simple = any(k in text_blob for k in ["crud", "admin", "management system", "simple"])

        if research_type == "AI / Machine Learning Research Proposal" or (has_ai_signal and has_ai_related_project):
            if has_eval_signal:
                return {
                    "recommended_level": "Possible journal submission after validation",
                    "reason": "The AI/ML proposal includes evaluation-oriented research signals, but the content still needs rigorous validation and reproducibility checks.",
                    "improvement_needed": "Add dataset transparency, baseline comparisons, proper model validation, and verified related literature before submission.",
                }
            return {
                "recommended_level": "Undergraduate research",
                "reason": "The AI/ML research direction is suitable for undergraduate research when supported by a defined dataset and evaluation plan.",
                "improvement_needed": "Add dataset transparency, model comparison baselines, and ethical risk assessment.",
            }
        if has_ai_signal or has_ai_related_project:
            return {
                "recommended_level": "Undergraduate research",
                "reason": "The project includes AI/ML-related signals, so undergraduate research dissemination is reasonable with careful evaluation.",
                "improvement_needed": "Add dataset transparency, model comparison baselines, and ethical risk assessment.",
            }
        if is_prototype:
            return {
                "recommended_level": "Local conference",
                "reason": "Prototype-stage outputs are usually strongest in local presentation venues.",
                "improvement_needed": "Strengthen implementation maturity and include broader validation before higher-tier submission.",
            }
        if is_simple:
            return {
                "recommended_level": "Capstone project",
                "reason": "Current system profile aligns with capstone-scale applied development work.",
                "improvement_needed": "Add comparative evaluation and measurable outcomes to improve publication readiness.",
            }

        if research_type == "System Development Research":
            return {
                "recommended_level": "Undergraduate research",
                "reason": "This system development study is suitable for undergraduate research or capstone presentation because it focuses on designing, developing, and evaluating an applied software solution.",
                "improvement_needed": "Add user evaluation, testing results, screenshots, system architecture, and verified related literature before submission.",
            }

        if research_type == "Feasibility Study":
            return {
                "recommended_level": "Capstone project",
                "reason": "A feasibility study is typically best positioned as a capstone or local presentation output focused on practical implementation readiness.",
                "improvement_needed": "Include cost estimates, technical assessment, schedule analysis, and validated constraints before presenting as a stronger academic output.",
            }

        return {
            "recommended_level": "Capstone project",
            "reason": "This research output is most suitable as a capstone-style academic draft unless stronger validation or experimental evidence is added.",
            "improvement_needed": "Improve evidence depth, testing quality, and citation-backed discussion before larger venues.",
        }
