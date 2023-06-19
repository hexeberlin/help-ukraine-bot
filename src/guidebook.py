"""Getting information from knowledge base in guidebook.yaml"""

import logging
from enum import Enum
from typing import Any, Dict, List, Optional

from yaml import safe_load

logger = logging.getLogger(__name__)


class NameType(str, Enum):
    accommodation: str = "accommodation"
    animal_help: str = "animals"
    apartments: str = "apartments"
    apartment_approval: str = "apartment_approval"
    beauty: str = "beauty"
    beschwerde: str = "beschwerde"
    cities: str = "cities"
    countries: str = "countries"
    deutschlandticket: str = "deutschlandticket"
    diplom: str = "diplom"
    education: str = "education"
    entertainment: str = "entertainment"
    evacuation: str = "evacuation"
    evacuation_cities: str = "evacuation_cities"
    food: str = "food"
    free_stuff: str = "free_stuff"
    furniture: str = "furniture"
    general_information: str = "general_information"
    german: str = "deutsch"
    handicap: str = "handicap"
    job_center_calc: str = "job_center_calc"
    jobs: str = "jobs"
    kindergeld: str = "kindergeld"
    leave: str = "leave"
    legal: str = "legal"
    medical: str = "medical"
    minors: str = "minors"
    no_ads: str = "no_ads"
    passport: str = "passport"
    lost_passport: str = "lost_passport"
    photo: str = "photo"
    pregnant: str = "pregnant"
    psychological: str = "psychological"
    qrcode: str = "qrcode"
    return_to_ukraine: str = "return_to_ukraine"
    rundfunk: str = "rundfunk"
    school: str = "school"
    schufa: str = "schufa"
    search: str = "search"
    simcards: str = "simcards"
    social_help: str = "social_help"
    statements: str = "official statements"
    taxis: str = "taxis"
    telegram_translation: str = "telegram_translation"
    translators: str = "translators"
    transport: str = "transport"
    vaccination: str = "vaccination"
    volunteer: str = "volunteer"
    university: str = "university"
    wbs: str = "wbs"


class Guidebook:
    """Class for the Guidebook"""

    def __init__(self, guidebook_path: str, vocabulary_path: str):
        with open(guidebook_path, "r") as f:
            guidebook = safe_load(f)

        self.guidebook = {k.lower(): v.get("contents") for k, v in guidebook.items()}
        self.description = {k.lower(): v.get("description") for k, v in guidebook.items()}

        with open(vocabulary_path, "r") as f:
            self.vocabulary = {
                alias.lower(): name.lower()
                for name, aliases in safe_load(f).items()
                for alias in aliases
            }

    @staticmethod
    def _format_results(info: str) -> str:
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
        return self._format_results(result)

    def _convert_dict_to_str(self, group_dict: Dict[str, Any]) -> str:
        result: str = ""
        for k, v in group_dict.items():
            result += k + ":\n"
            for value in v:
                result += "- " + value + "\n"
        return self._format_results(result)

    def get_info(self, group_name: str, name: Optional[str] = None) -> str:
        group = self.guidebook.get(group_name.lower())
        if group:
            if isinstance(group, dict):
                group_lower = {k.lower(): v for k, v in group.items()}
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
        return self.get_info(group_name=NameType[group_name], name=name)

    def get_cities(self, group_name: Enum = NameType.cities, name: str = None) -> str:
        if not name:
            return self._format_results(
                "Пожалуйста, уточните название города: /cities Name\n"
            )
        if name in self.vocabulary:
            return self.get_info(
                group_name=group_name.value, name=self.vocabulary.get(name)
            )
        return self.get_info(group_name=group_name.value, name=name)

    def get_countries(
        self, group_name: Enum = NameType.countries, name: Optional[str] = None
    ) -> str:
        if not name:
            return self._format_results(
                "Пожалуйста, уточните название страны: /countries Name\n"
            )
        return self.get_info(group_name=group_name.value, name=name)
