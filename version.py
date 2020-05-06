import json


def increase_build_version():
    data = None
    with open("digicubes_rest/version.json") as f:
        data = json.load(f)

    print(data)
    data["version"][2] += 1
    print(data)
    with open("digicubes_rest/version.json", "w") as f:
        json.dump(data, f, indent=2)


if __name__ == "__main__":
    increase_build_version()
