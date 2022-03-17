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


def load_vocabulary():
    with open("vocabulary.yml", "r") as stream:
        try:
            vocabulary = CaseInsensitiveDict(yaml.safe_load(stream))
            new_vocabulary = CaseInsensitiveDict()
            for k, v in vocabulary.items():
                for i in v:
                    new_vocabulary[i] = k
            return new_vocabulary
        except yaml.YAMLError as exc:
            print(exc)


def convert_dict_to_string(info, group_name):
    result = "============================\n"
    result += "результаты для %s" %(group_name)
    for key, value in info.items():
        result += key + " :\n"
        for s in value:
            result += "- " + s + "\n"
        result += "\n"

    return result + "\n============================"


def convert_list_to_string(info, group_name, name):
    result = "============================\n"
    result += "вы искали %s в %s \n" % (name, group_name)
    for s in info:
        result += s + "\n"
    return result + "\n============================"


def get_info(guidebook: CaseInsensitiveDict, group_name: str, name: str = None):
    group_dict = CaseInsensitiveDict(guidebook[group_name])

    if name is None:
        return convert_dict_to_string(group_dict, group_name)
    else:
        if name in group_dict:
            return convert_list_to_string(group_dict[name], group_name, name)
        else:
            if group_name == "cities":
                return "К сожалению, мы пока не располагаем этой информацией по городу %s" % (name)
            else:
                return convert_dict_to_string(group_dict)


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
