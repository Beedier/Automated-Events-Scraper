from dotenv import dotenv_values

_config = dotenv_values('.env')


def get_config():
    """Return the loaded configuration (for external access)"""
    return _config
