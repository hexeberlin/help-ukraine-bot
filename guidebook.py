import logging
from requests.structures import CaseInsensitiveDict
import yaml

logger = logging.getLogger(__name__)


def load_guidebook():
    with open("guidebook.yml", "r") as stream:
        try:
            guidebook = CaseInsensitiveDict(yaml.safe_load(stream))
            return guidebook
        except yaml.YAMLError as exc:
            print(exc)


def convert_dict_to_string(info):
    result = "============================\n"
    for key, value in info.items():
        result += key + " :\n"
        for s in value:
            result += "- " + s + "\n"
        result += "\n"

    return result + "\n============================"


def convert_list_to_string(info):
    result = "============================\n"
    for s in info:
        result += s + "\n"
    return result + "\n============================"


def get_info(guidebook, group_name, name=None):
    dict = guidebook[group_name]

    if name is None:
        return convert_dict_to_string(dict)
    else:
        key_dict = {k.lower(): k for k, v in dict.items()}
        if name in key_dict:
            return convert_list_to_string(dict[key_dict[name]])
        else:
            if group_name == "cities":
                return "К сожалению, мы пока не располагаем этой информацией"
            else:
                return convert_dict_to_string(dict)


def evacuation(guidebook):
    return convert_dict_to_string(guidebook["evacuation"])


def taxis(guidebook):
    taxis = guidebook["taxis"]
    return convert_list_to_string(taxis)


def germany_domestic(
    guidebook: CaseInsensitiveDict, group_name: str, name: str = None
) -> str:
    guidebook_dict = guidebook[group_name]
    if guidebook_dict:
        if not name:
            hint = (
                "\nПожалуйста, уточните название федеративной земли: \n"
                "/germany_domestic Name"
            )
            return guidebook_dict["general"][0] + hint
        return guidebook_dict[name][0]
