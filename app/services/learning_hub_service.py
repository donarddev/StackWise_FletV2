"""Learning Hub topic service."""

from __future__ import annotations

from collections import Counter

from app.data.learning_hub_topics import learning_topics


class LearningHubService:
    _CATEGORY_ALIASES = {
        "all topics": None,
        "all": None,
        "languages": "language",
        "language": "language",
        "frameworks": "framework",
        "framework": "framework",
        "sdlc models": "sdlc",
        "sdlc": "sdlc",
    }

    def get_all_topics(self) -> list[dict]:
        return list(learning_topics)

    def get_topics_by_category(self, category: str) -> list[dict]:
        normalized = self._normalize_category(category)
        if normalized is None:
            return self.get_all_topics()
        return [topic for topic in learning_topics if topic.get("category") == normalized]

    def search_topics(self, query: str, category: str | None = None) -> list[dict]:
        query_text = (query or "").strip().lower()
        scoped_topics = self.get_topics_by_category(category or "All topics")
        if not query_text:
            return scoped_topics

        result: list[dict] = []
        for topic in scoped_topics:
            searchable = [
                topic.get("name", ""),
                topic.get("category", ""),
                topic.get("difficulty", ""),
                topic.get("description", ""),
                topic.get("best_for", ""),
                topic.get("recommended_when", ""),
                topic.get("avoid_when", ""),
                " ".join(topic.get("tags", [])),
                " ".join(topic.get("common_frameworks", [])),
                " ".join(topic.get("learning_path", [])),
            ]
            if query_text in " ".join(searchable).lower():
                result.append(topic)
        return result

    def count_by_category(self) -> dict[str, int]:
        counts = Counter(topic.get("category", "") for topic in learning_topics)
        return {
            "languages": counts.get("language", 0),
            "frameworks": counts.get("framework", 0),
            "sdlc_models": counts.get("sdlc", 0),
        }

    def _normalize_category(self, category: str | None) -> str | None:
        if category is None:
            return None
        return self._CATEGORY_ALIASES.get(category.strip().lower(), None)
