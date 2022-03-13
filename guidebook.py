import yaml
import logging
from requests.structures import CaseInsensitiveDict

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

    return result + "\n============================"


def convert_list_to_string(info):
    result = "============================\n"
    for s in info:
        result += s + "\n"
    return result + "\n============================"


def get_info(guidebook, group_name, name):
    dict = guidebook[group_name]

    key_dict = {k.lower(): k for k, v in dict.items()}
    if name in key_dict:
        return convert_list_to_string(dict[key_dict[name]])
    else:
        return "К сожалению, мы пока не располагаем этой информацией"


def evacuation(guidebook):
    return convert_dict_to_string(guidebook["evacuation"])


def taxis(guidebook):
    taxis = guidebook["taxis"]
    return convert_list_to_string(taxis)

# if __name__ == "__main__":
#     guidebook = load_guidebook()
#     countries_chats(guidebook, "poland")
