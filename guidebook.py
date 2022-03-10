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


def cities(guidebook, name=None):
    if name is None:
        return convert_dict_to_string(guidebook["cities"])
    else:
        key_dict = {k.lower(): k for k, v in guidebook["cities"].items()}
        if name in key_dict:
            return convert_list_to_string(guidebook["cities"][key_dict[name]])
        else:
            return convert_dict_to_string(guidebook["cities"])


def countries(guidebook, name=None):
    if name is None:
        return convert_dict_to_string(guidebook["countries"])
    else:
        if (name in guidebook["countries"]):
            return convert_list_to_string(guidebook["countries"][name])
        else:
            return convert_dict_to_string(guidebook["countries"])


def evacuation(guidebook):
    return convert_dict_to_string(guidebook["evacuation"])


def evacuation_cities(guidebook, name=None):
    if name is None:
        return convert_dict_to_string(guidebook["evacuation_cities"])
    else:
        if (name in guidebook["evacuation_cities"]):
            return convert_list_to_string(guidebook["evacuation_cities"][name])
        else:
            return convert_dict_to_string(guidebook["evacuation_cities"])


if __name__ == "__main__":
    test_str = "/cities leipzig"
    name = test_str.split(" ")[1].strip()
    guidebook = load_guidebook()
    result = cities(guidebook, name)
    print(result)
