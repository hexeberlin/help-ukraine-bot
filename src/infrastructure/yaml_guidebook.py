"""YAML-based guidebook implementation."""

import logging
from typing import Any, Dict, List, Optional

from yaml import safe_load

logger = logging.getLogger(__name__)


class YamlGuidebook:
    """YAML-based implementation of guidebook data access."""

    def __init__(self, guidebook_path: str, vocabulary_path: str):
        with open(guidebook_path, "r", encoding="utf-8") as f:
            guidebook = safe_load(f)

        self.guidebook = {k.lower(): v.get("contents") for k, v in guidebook.items()}
        self.descriptions = {k.lower(): v.get("description") for k, v in guidebook.items()}

        # Cache lowercase versions of dict keys to avoid rebuilding on every get_info() call
        self._guidebook_lower_cache = {
            k: {inner_k.lower(): inner_v for inner_k, inner_v in v.items()}
            for k, v in self.guidebook.items()
            if isinstance(v, dict)
        }

        with open(vocabulary_path, "r", encoding="utf-8") as f:
            self.vocabulary = {
                alias.lower(): name.lower()
                for name, aliases in safe_load(f).items()
                for alias in aliases
            }

    @staticmethod
    def format_results(info: str) -> str:
        separator: str = "=" * 30
        return separator + "\n" + info + separator

    def _convert_list_to_str(
        self, group_list: List[str], name: Optional[str] = None
    ) -> str:
        if name:
            result = f"{name.title()}\n"
        else:
            result = ""
        for item in group_list:
            result += item + "\n"
        return self.format_results(result)

    def _convert_dict_to_str(self, group_dict: Dict[str, Any]) -> str:
        result: str = ""
        for k, v in group_dict.items():
            result += k + ":\n"
            for value in v:
                result += "- " + value + "\n"
        return self.format_results(result)

    def get_info(self, group_name: str, name: Optional[str] = None) -> str:
        group = self.guidebook.get(group_name.lower())
        if group:
            if isinstance(group, dict):
                group_lower = self._guidebook_lower_cache.get(group_name.lower())
                if name:
                    if name.lower() not in group_lower.keys():
                        return (
                            "К сожалению, мы пока не располагаем информацией "
                            + f"по запросу {group_name}, {name}."
                        )
                    return self._convert_list_to_str(group_lower[name.lower()], name)
                return self._convert_dict_to_str(group)
            if isinstance(group, List):
                return self._convert_list_to_str(group)
        return (
            "К сожалению, мы пока не располагаем информацией "
            + f"по запросу {group_name}."
        )

    def get_results(self, group_name: str, name: str = None) -> str:
        return self.get_info(group_name=group_name, name=name)

    def get_cities(self, group_name: str = "cities", name: str = None) -> str:
        if not name:
            return self.format_results(
                "Пожалуйста, уточните название города: /cities Name\n"
            )
        if name in self.vocabulary:
            return self.get_info(
                group_name=group_name, name=self.vocabulary.get(name)
            )
        return self.get_info(group_name=group_name, name=name)

    def get_countries(
        self, group_name: str = "countries", name: Optional[str] = None
    ) -> str:
        if not name:
            return self.format_results(
                "Пожалуйста, уточните название страны: /countries Name\n"
            )
        return self.get_info(group_name=group_name, name=name)

    def get_topics(self) -> List[str]:
        """Get list of all available topics."""
        return list(self.guidebook.keys())

    def get_descriptions(self) -> Dict[str, str]:
        """Get topic descriptions."""
        return self.descriptions.copy()
