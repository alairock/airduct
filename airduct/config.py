import os
import yaml


def getenv(name, default=None):
    env_prefix = os.getenv('ENV_PREFIX', '')
    value = os.getenv(env_prefix + name, default)

    c = os.environ.get('AIRDUCT_CONFIG_FILE')
    with open(c) as file:
        config = yaml.load(file, Loader=yaml.FullLoader)

    config_file_value = config
    name_split = name.split('_')
    for index, v in enumerate(name_split):
        config_file_value = config_file_value.get(v.lower(), None if index + 1 == len(name_split) else {})

    if config_file_value is None:
        return value
    return config_file_value
