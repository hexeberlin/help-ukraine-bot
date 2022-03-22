"""Getting information from knowledge base in guidebook.yaml"""

from abc import ABC
from enum import Enum
import logging
from typing import Any, Dict, List, Optional
import toml
from yaml import safe_load, YAMLError

logger = logging.getLogger(__name__)
settings: Dict[str, str] = toml.load("settings.toml")


class NameType(str, Enum):
    animal_help: str = "animals"
    cities: str = "cities"
    countries: str = "countries"
    dentist: str = "dentist"
    evacuation: str = "evacuation"
    evacuation_cities: str = "evacuation_cities"
    freestuff: str = "freestuff"
    german: str = "deutsch"
    germany_domestic: str = "germany_domestic"
    homesharing: str = "homesharing"
    humanitarian: str = "humanitarian"
    jobs: str = "jobs"
    medical: str = "medical"
    taxis: str = "taxis"
    travel: str = "travel"
    volunteer: str = "volunteer"
    disabled: str = "disabled"


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

    def get_animal_help(self, group_name: Enum = NameType.animal_help) -> str:
        return self._get_info(group_name=group_name)

    def get_cities(
        self,
        group_name: Enum = NameType.cities,
        name: str = None
    ) -> str:
        if not name:
            return self._format_results(
                "Пожалуйста, уточните название города: /cities Name\n"
                )
        return self._get_info(group_name=group_name, name=name)

    def get_cities_all(self, group_name: Enum = NameType.cities) -> str:
        return self._get_info(group_name=group_name)

    def get_countries(
        self, group_name: Enum = NameType.countries, name: Optional[str] = None
    ) -> str:
        vocabulary = self.get_vocabulary()
        if name:
            if name in vocabulary:
                return self._get_info(group_name=group_name,
                                    name=vocabulary.get(name))
            return (
                "К сожалению, мы пока не располагаем информацией по запросу "
                +f"{group_name.value}, {name}."
            )
        else:
            return self._get_info(group_name=group_name)

    def get_dentist(self, group_name: Enum = NameType.dentist) -> str:
        return self._get_info(group_name=group_name)

    def get_german(self, group_name: Enum = NameType.german) -> str:
        return self._get_info(group_name=group_name)

    def get_evacuation(self, group_name: Enum = NameType.evacuation) -> str:
        return self._get_info(group_name=group_name)

    def get_evacuation_cities(
        self,
        group_name: Enum = NameType.evacuation_cities,
        name: Optional[str] = None
    ) -> str:
        return self._get_info(group_name=group_name, name=name)

    def get_freestuff(
        self,
        group_name: Enum = NameType.freestuff,
        name: Optional[str] = None
    ) -> str:
        return self._get_info(group_name=group_name, name=name)

    def get_germany_domestic(
        self,
        group_name: Enum = NameType.germany_domestic,
        name: Optional[str] = None
    ) -> str:
        if not name:
            hint = (
                "\nПожалуйста, уточните название федеративной земли: \n"
                "/germany_domestic Name"
            )
            return self._get_info(group_name, "Регистрация") + hint
        vocabulary = self.get_vocabulary()
        if name in vocabulary:
            return self._get_info(group_name=group_name,
                                  name=vocabulary.get(name))
        return (
            "К сожалению, мы пока не располагаем информацией по запросу "
            +f"{group_name.value}, {name}."
        )
    def get_homesharing(self, group_name: Enum = NameType.homesharing) -> str:
        return self._get_info(group_name=group_name)

    def get_humanitarian(self, group_name: Enum = NameType.humanitarian) -> str:
        return self._get_info(group_name=group_name)

    def get_jobs(self, group_name: Enum = NameType.jobs) -> str:
        return self._get_info(group_name=group_name)

    def get_medical(
        self, group_name: Enum = NameType.medical, name: Optional[str] = None
    ) -> str:
        return self._get_info(group_name=group_name, name=name)

    def get_taxis(self, group_name: Enum = NameType.taxis) -> str:
        return self._get_info(group_name=group_name)

    def get_travel(self, group_name: Enum = NameType.travel) -> str:
        return self._get_info(group_name=group_name)

    def get_volunteer(self, group_name: Enum = NameType.volunteer) -> str:
        return self._get_info(group_name=group_name)

    def get_disabled(self, group_name: Enum = NameType.disabled) -> str:
        return self._get_info(group_name=group_name)
