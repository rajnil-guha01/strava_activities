from pathlib import Path

def get_config_file_path(config_file_name: str) -> str:
    """
    Get the absolute path of the configuration file.
    Parameters:
    - config_file_name (str): Name of the configuration file.
    Returns:
    - str: Absolute path of the configuration file.
    """
    base_path = Path(__file__).parent.parent.resolve()
    config_file_path = base_path / 'resources' / 'config' / config_file_name
    return config_file_path
