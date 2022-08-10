"""Getting information from knowledge base in guidebook.yaml"""

import logging
from abc import ABC
from enum import Enum
from typing import Any, Dict, List, Optional

import toml
from yaml import safe_load, YAMLError

logger = logging.getLogger(__name__)
settings: Dict[str, str] = toml.load("settings.toml")


class NameType(str, Enum):
    accommodation: str = "accommodation"
    animal_help: str = "animals"
    apartments: str = "apartments"
    banking: str = "banking"
    beauty: str = "beauty"
    berlinpass: str = "berlinpass"
    beschwerde: str = "beschwerde"
    cities: str = "cities"
    disabled: str = "disabled"
    countries: str = "countries"
    education: str = "education"
    entertainment: str = "entertainment"
    euro_9: str = "euro_9"
    evacuation: str = "evacuation"
    evacuation_cities: str = "evacuation_cities"
    food: str = "food"
    free_stuff: str = "free_stuff"
    general_information: str = "general_information"
    german: str = "deutsch"
    handbook: str = "handbook"
    hryvnia: str = "hryvnia"
    jobs: str = "jobs"
    kindergeld: str = "kindergeld"
    leave: str = "leave"
    legal: str = "legal"
    medical: str = "medical"
    meetup: str = "meetup"
    minors: str = "minors"
    moving: str = "moving"
    no_ads: str = "no_ads"
    photo: str = "photo"
    pregnant: str = "pregnant"
    psychological: str = "psychological"
    rundfunk: str = "rundfunk"
    school: str = "school"
    schufa: str = "schufa"
    simcards: str = "simcards"
    social_adaptation: str = "social_adaptation"
    social_help: str = "social_help"
    statements: str = "official statements"
    taxis: str = "taxis"
    telegram_translation: str = "telegram_translation"
    translators: str = "translators"
    transport: str = "transport"
    vaccination: str = "vaccination"
    volunteer: str = "volunteer"
    uni: str = "university"
    wbs: str = "wbs"


class Guidebook(ABC):
    """Class for the Guidebook"""

    def __init__(self):
        self.guidebook: Dict[str, Any] = None
        self.vocabulary: Dict[str, Any] = None

    def _get_guidebook(self) -> Dict[str, Any]:
        path = settings["GUIDEBOOK_PATH"]
        with open(path, "r") as stream:
            try:
                self.guidebook = safe_load(stream)
            except YAMLError as err:
                logger.error("Yaml error", err)
                raise err
            return {k.lower(): v for k, v in self.guidebook.items()}

    @staticmethod
    def get_vocabulary() -> Dict[Any, Any]:
        path = settings["VOCABULARY_PATH"]
        with open(path, "r") as stream:
            try:
                vocabulary = safe_load(stream)
            except YAMLError as err:
                logger.error(**err.__dict__)
                raise err
            new_vocabulary = dict()
            for k, v in vocabulary.items():
                for i in v:
                    new_vocabulary[i.lower()] = k.lower()
            return new_vocabulary

    @staticmethod
    def _format_results(info: str) -> str:
        separator: str = "=" * 30
        return separator + "\n" + info + separator

    def _convert_list_to_str(
            self,
            group_list: List[str],
            name: Optional[str] = None
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

    def _get_info(self, group_name: Enum, name: Optional[str] = None) -> str:
        group = self._get_guidebook().get(group_name.value.lower())
        if group:
            if isinstance(group, dict):
                group_lower = {k.lower(): v for k, v in group.items()}
                if name:
                    if name.lower() not in group_lower.keys():
                        return (
                                "К сожалению, мы пока не располагаем информацией "
                                + f"по запросу {group_name.value}, {name}."
                        )
                    return self._convert_list_to_str(group_lower[name.lower()],
                                                     name)
                return self._convert_dict_to_str(group)
            # if group has type list
            return self._convert_list_to_str(group)
        return (
                "К сожалению, мы пока не располагаем информацией "
                + f"по запросу {group_name.value}."
        )

    def get_results(self, group_name: str, name: str = None) -> str:
        return self._get_info(group_name=NameType[group_name], name=name)

    def get_cities(
            self,
            group_name: Enum = NameType.cities,
            name: str = None
    ) -> str:
        if not name:
            return self._format_results(
                "Пожалуйста, уточните название города: /cities Name\n"
            )
        vocabulary = self.get_vocabulary()
        if name in vocabulary:
            return self._get_info(group_name=group_name,
                                  name=vocabulary.get(name))
        return self._get_info(group_name=group_name, name=name)

    def get_countries(
            self, group_name: Enum = NameType.countries, name: Optional[str] = None
    ) -> str:
        if not name:
            return self._format_results(
                "Пожалуйста, уточните название страны: /cities Name\n"
            )
        return self._get_info(group_name=group_name, name=name)

    def get_meetup(
            self, group_name: Enum = NameType.meetup, name: Optional[str] = None
    ) -> str:
        vocabulary = self.get_vocabulary()
        if name in vocabulary:
            return self._get_info(group_name=group_name,
                                  name=vocabulary.get(name))
        return self._get_info(group_name=group_name, name=name)
