"""
This module contains helper functions.
"""
import yaml


def dict_to_dataclass(to_dataclass, from_dict):
    """
    Converts a dictionary to a dataclass.
    """
    for key, value in from_dict.items():
        setattr(to_dataclass, key, value)


def read_config(path="gitssues.yml"):
    """
    Reads the configuration file.
    """
    with open(path) as f:
        return yaml.full_load(f)
