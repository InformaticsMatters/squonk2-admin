"""A holder of the Squonk2 Environment instance.
"""
from typing import List, Optional

from squonk2.environment import Environment

_ENVIRONMENT: Optional[Environment] = None


def set_environment(chosen_env: Environment) -> None:
    """Sets the environment, expected to be called once from the program entry point."""
    global _ENVIRONMENT  # pylint: disable=global-statement
    _ENVIRONMENT = chosen_env


def get_environment() -> Environment:
    """Gets the environment, expected to have been set.
    If not set an attempt to get the default environment is made.
    """
    if _ENVIRONMENT:
        return _ENVIRONMENT

    names: List[str] = Environment.load()
    assert names
    return Environment(names[0])
