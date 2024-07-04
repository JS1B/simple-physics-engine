import json

from .key_mappings import KeyMappings


def load_key_mappings(config_file):
    with open(config_file, "r") as file:
        data = json.load(file)
    return KeyMappings.from_dict(data)
