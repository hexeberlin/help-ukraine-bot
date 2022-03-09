import yaml


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
        if (name in guidebook["cities"]):
            return convert_list_to_string(guidebook["cities"][name])
        else:
            return convert_dict_to_string(guidebook["cities"])

if __name__ == "__main__":
    guidebook = load_guidebook()
    print(cities(guidebook, ""))
