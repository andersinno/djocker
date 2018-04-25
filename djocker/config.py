import os
from types import SimpleNamespace

from six.moves import configparser

CONFIG_SECTION = 'djocker'


def default_config_values():
    return {
        'python_bin': 'python3',
        'compose_service_name': 'api'
    }


def get_config_parser():
    file_path = os.path.join('.', 'setup.cfg')

    parser = configparser.ConfigParser(allow_no_value=True)
    parser.read(file_path)

    return parser


def get_djocker_config():
    djocker_config = default_config_values()
    parser = get_config_parser()

    if not parser.has_section('djocker'):
        return SimpleNamespace(**djocker_config)

    config_keys = djocker_config.keys()

    for key in config_keys:
        djocker_config[key] = parser[CONFIG_SECTION].get(key, djocker_config[key])

    return SimpleNamespace(**djocker_config)


config = get_djocker_config()
