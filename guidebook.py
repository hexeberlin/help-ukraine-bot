import yaml

def load_guidebook():
    with open("guidebook.yml", "r") as stream:
        try:
            guidebook = yaml.safe_load(stream)
            return guidebook
        except yaml.YAMLError as exc:
            print(exc)


def cities(guidebook, name):
    if len(name) == 0:
        return guidebook["cities"]
    else:
        return guidebook["cities"][name]


if __name__ == "__main__":
    guidebook = load_guidebook()
    print(cities(guidebook, "Berlin"))