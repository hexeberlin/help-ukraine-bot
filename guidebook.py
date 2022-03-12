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
    result = ""
    for key, value in info.items():
        result += key + " :\n"
        for s in value:
            result += "- " + s + "\n"

    return result


def convert_list_to_string(info):
    result = ""
    for s in info:
        result += s + "\n"
    return result


def get_info(dict, name):
    if name is None:
        return convert_dict_to_string(dict)
    else:
        key_dict = {k.lower(): k for k, v in dict.items()}
        if name in key_dict:
            return convert_list_to_string(dict[key_dict[name]])
        else:
            return convert_dict_to_string(dict)


def cities_chats(guidebook, name=None):
    cities = guidebook["cities"]
    return get_info(cities, name)


def countries_chats(guidebook, name=None):
    countries = guidebook["countries"]
    return get_info(countries, name)


def evacuation(guidebook):
    return convert_dict_to_string(guidebook["evacuation"])


def evacuation_cities(guidebook, name=None):
    evac_cities = guidebook["evacuation_cities"]
    return get_info(evac_cities, name)


if __name__ == "__main__":
    guidebook = load_guidebook()
    countries_chats(guidebook, "poland")
