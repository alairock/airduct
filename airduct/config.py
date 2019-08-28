import os
import yaml
from airduct import logger

ENV_CONFIG = None


def getenv(name, default=None):
    global ENV_CONFIG
    env_prefix = os.getenv('ENV_PREFIX', '')
    value = os.getenv(env_prefix + name)
    if value is not None:
        return value

    c = os.environ.get('AIRDUCT_CONFIG_FILE')
    config_file_value = ENV_CONFIG
    if ENV_CONFIG is None:
        try:
            with open(c) as file:
                ENV_CONFIG = yaml.load(file, Loader=yaml.FullLoader) or {}
                config_file_value = ENV_CONFIG
        except FileNotFoundError:
            ENV_CONFIG = {}
            config_file_value = {}
            logger.logger.info(
                f'Config file not found {c}, will attempt to use env vars.')

    name_split = name.split('_')
    for index, v in enumerate(name_split):
        config_file_value = config_file_value.get(v.lower(), None if index + 1 == len(name_split) else {})

    if config_file_value is None:
        return default
    return config_file_value
