"""Reusable Ollama client for local Llama generation."""

from __future__ import annotations

import json
from typing import Any

import httpx

from app.config.ai_config import AIConfig
from app.utils.logger import get_logger

log = get_logger(__name__)

TAGS_PATH = "/api/tags"
GENERATE_PATH = "/api/generate"


class OllamaService:
    def __init__(self, config: AIConfig | None = None) -> None:
        self.config = config or AIConfig()

    def check_ollama_available(self) -> dict[str, Any]:
        try:
            with httpx.Client(timeout=5.0) as client:
                response = client.get(f"{self.config.base_url}{TAGS_PATH}")
                if response.status_code != 200:
                    return {
                        "success": False,
                        "error": "Ollama is not running or unreachable.",
                        "error_type": "unreachable",
                        "models": [],
                        "model_found": False,
                    }

                payload = response.json()
                models = self._extract_model_names(payload)
                model_found = self._model_is_available(models)
                if not model_found:
                    return {
                        "success": False,
                        "error": f"The {self.config.model} model is not installed. Run: ollama pull {self.config.model}",
                        "error_type": "model_missing",
                        "models": models,
                        "model_found": False,
                    }

                return {"success": True, "models": models, "model_found": True}
        except httpx.TimeoutException:
            return {
                "success": False,
                "error": "Ollama is not running or unreachable.",
                "error_type": "timeout",
                "models": [],
                "model_found": False,
            }
        except Exception as exc:
            log.info("Ollama availability check failed: %s", exc)
            return {
                "success": False,
                "error": "Ollama is not running or unreachable.",
                "error_type": "unreachable",
                "models": [],
                "model_found": False,
            }

    def generate(self, prompt: str, *, prefer_json_format: bool = True) -> dict[str, Any]:
        if prefer_json_format:
            attempts = [
                {"use_json_format": True, "include_options": True},
                {"use_json_format": True, "include_options": False},
                {"use_json_format": False, "include_options": False},
            ]
        else:
            attempts = [{"use_json_format": False, "include_options": True}, {"use_json_format": False, "include_options": False}]

        last_result: dict[str, Any] = {"success": False, "error_type": "unknown", "error": "Ollama request failed."}
        for attempt_index, attempt in enumerate(attempts):
            result = self._post_generate(
                prompt,
                use_json_format=attempt["use_json_format"],
                include_options=attempt["include_options"],
            )
            if result.get("success"):
                result["used_json_format"] = attempt["use_json_format"]
                result["used_options"] = attempt["include_options"]
                if attempt_index > 0:
                    result["retried"] = True
                return result
            last_result = result

        return last_result

    def _post_generate(self, prompt: str, *, use_json_format: bool, include_options: bool) -> dict[str, Any]:
        try:
            with httpx.Client(timeout=self.config.request_timeout_seconds) as client:
                payload: dict[str, Any] = {
                    "model": self.config.model,
                    "prompt": prompt,
                    "stream": False,
                }
                if include_options:
                    payload["options"] = {
                        "temperature": 0.2,
                        "top_p": 0.9,
                        "num_ctx": self.config.num_ctx,
                        "num_predict": self.config.num_predict,
                    }
                if use_json_format:
                    payload["format"] = "json"

                response = client.post(f"{self.config.base_url}{GENERATE_PATH}", json=payload)
                response.raise_for_status()
                status_code = response.status_code
                payload = response.json()
                response_text = str(payload.get("response") or "").strip()
                if not response_text:
                    return {
                        "success": False,
                        "error": "Ollama responded, but the response was empty.",
                        "error_type": "empty_response",
                        "status_code": status_code,
                    }
                return {
                    "success": True,
                    "response_text": response_text,
                    "response_json": payload,
                    "used_json_format": use_json_format,
                    "status_code": status_code,
                }
        except httpx.TimeoutException as exc:
            return {
                "success": False,
                "error": "Ollama took too long to generate the research draft. Try shorter inputs or regenerate.",
                "error_type": "timeout",
            }
        except httpx.ConnectError:
            return {
                "success": False,
                "error": "Ollama is not running. Please run `ollama serve`.",
                "error_type": "connection_refused",
            }
        except Exception as exc:
            error_text = str(exc)
            lower = error_text.lower()
            if "connection" in lower or "refused" in lower or "connect" in lower:
                return {
                    "success": False,
                    "error": "Ollama is not running. Please run `ollama serve`.",
                    "error_type": "connection_refused",
                }
            return {
                "success": False,
                "error": f"Research generation failed: {self._short_error(error_text)}",
                "error_type": "request_error",
            }

    @staticmethod
    def extract_json_block(text: str) -> str:
        raw = (text or "").strip()
        if not raw:
            return ""
        if raw.startswith("```json"):
            raw = raw.removeprefix("```json").strip()
        if raw.startswith("```"):
            raw = raw.removeprefix("```").strip()
        if raw.endswith("```"):
            raw = raw[: -3].strip()
        if raw.startswith("{") and raw.endswith("}"):
            return raw
        start = raw.find("{")
        end = raw.rfind("}")
        if start >= 0 and end > start:
            return raw[start : end + 1]
        return raw

    @staticmethod
    def parse_json(text: str) -> dict[str, Any] | None:
        try:
            parsed = json.loads(text)
            return parsed if isinstance(parsed, dict) else None
        except Exception:
            return None

    @staticmethod
    def _extract_model_names(payload: Any) -> list[str]:
        models: list[str] = []
        if not isinstance(payload, dict):
            return models
        raw_models = payload.get("models")
        if not isinstance(raw_models, list):
            return models
        for item in raw_models:
            if isinstance(item, dict):
                name = str(item.get("name") or "").strip()
                if name:
                    models.append(name)
        return models

    def _model_is_available(self, models: list[str]) -> bool:
        wanted = self.config.model.strip()
        return any(model == wanted or model.startswith(f"{wanted}:") for model in models)

    @staticmethod
    def _short_error(error_text: str, limit: int = 180) -> str:
        text = str(error_text or "").strip()
        if len(text) <= limit:
            return text
        return text[: limit - 3].rstrip() + "..."
