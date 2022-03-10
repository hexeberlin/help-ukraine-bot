import yaml
import logging

logger = logging.getLogger(__name__)


def load_guidebook():
    with open("guidebook.yml", "r") as stream:
        try:
            guidebook = yaml.safe_load(stream)
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
        logger.info("cities name:" + name)
        if name in guidebook["cities"]:
            logger.info("cities name:" + name)
            return convert_list_to_string(guidebook["cities"][name])
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


# if __name__ == "__main__":
#     test_str = "/cities Leipzig"
#     name = test_str.split(" ")[1].strip()
#     guidebook = load_guidebook()
#     result = cities(guidebook, name)
#     print(result)