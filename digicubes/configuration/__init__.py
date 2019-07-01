import json

class Configuration():

    @classmethod
    def init_from_file(cls, filename="configuration.json"):
        with open(filename, 'r') as conf_file:
            data = json.load(conf_file)

