from typing import Callable
from configparser import ConfigParser, NoSectionError, NoOptionError


def read_asset_config(config: ConfigParser, key: bytes, decrypt: Callable):
    try:
        section = config['credentials']
    except NoSectionError:
        raise Exception(f'Missing section [credentials]')

    try:
        username = section.get('username')
    except NoOptionError:
        raise Exception(f'Missing username')

    try:
        password_encrypted = section.get('password')
    except NoOptionError:
        raise Exception(f'Missing password')

    try:
        password = decrypt(key, password_encrypted)
    except Exception:
        raise Exception(f'Failed to decrypt password')

    return {
        'credentials': {
            'username': username,
            'password': password,
        }
    }