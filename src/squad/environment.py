"""Environment module.

Reads the environment file exposing the values for the chosen environment.
"""
import os
from typing import Any, Dict, Optional

from yaml import FullLoader, load

# The environments file (YAML) is typically expected in the user's '~/.squonk2'
# directory. It contains 'environments' that define the connection details
# for the various Keycloak, Data Manager and Account Server services.
# This default is replaced with the value of the environment variable
# 'SQUONK2_ENVIRONMENTS_FILE'.
#
# See the project's 'environments' file for an example of the content of the file.
_ENVIRONMENT_DIRECTORY: str = "~/.squonk2"
_ENVIRONMENT_FILE: str = os.environ.get(
    "SQUONK2_ENVIRONMENTS_FILE", f"{_ENVIRONMENT_DIRECTORY}/environments"
)

# The key for the block of environments
_ENVIRONMENTS_KEY: str = "environments"
# The key for the 'default' environment
_DEFAULT_KEY: str = "default"

# Keys required in each environment.
_KEYCLOAK_HOSTNAME_KEY: str = "keycloak-hostname"
_KEYCLOAK_REALM_KEY: str = "keycloak-realm"
_KEYCLOAK_DM_CLIENT_ID_KEY: str = "keycloak-dm-client-id"
_DM_HOSTNAME_KEY: str = "dm-hostname"
_ADMIN_USER_KEY: str = "admin-user"
_ADMIN_PASSWORD_KEY: str = "admin-password"
# Optional keys
_KEYCLOAK_AS_CLIENT_ID_KEY: str = "keycloak-as-client-id"
_AS_HOSTNAME_KEY: str = "as-hostname"


class Environment:
    """Loads the values from the environment file for the given envrionment."""

    # Location of the file
    __environments_file: str = os.path.expandvars(os.path.expanduser(_ENVIRONMENT_FILE))
    # The environment to use.
    # This is ether the value of the 'deafult' in the file or the
    # 'name' passed into our init() method.
    __environment: str = ""
    # Dictionary-form of the entire file
    __config: Dict[str, Any] = {}

    # Values extracted from the chosen environment
    __keycloak_hostname: str = ""
    __keycloak_realm: str = ""
    __keycloak_dm_client_id: str = ""
    __dm_hostname: str = ""
    __admin_user: str = ""
    __admin_password: str = ""
    __keycloak_as_client_id: Optional[str] = None
    __as_hostname: Optional[str] = None

    @classmethod
    def init(cls, name: Optional[str] = None) -> None:
        """Initialisation - loads the environment file,
        returning values from the environment that's passed in or
        named in the 'default' key in the file.
        """
        # Regardless, if there is no default environment directory, create one.
        # During CI this will fail, so we avoid creating the
        # directory if CI is set.
        if not os.environ.get("CI"):
            os.makedirs(os.path.expanduser(_ENVIRONMENT_DIRECTORY), exist_ok=True)

        if not os.path.exists(Environment.__environments_file):
            raise Exception(f"{Environment.__environments_file} does not exist")
        with open(Environment.__environments_file, encoding="utf8") as config_file:
            Environment.__config = load(config_file, Loader=FullLoader)
        # Does it look like YAML?
        if not Environment.__config:
            raise Exception(f"{Environment.__environments_file} is empty")
        if not isinstance(Environment.__config, dict):
            raise Exception(
                f"{Environment.__environments_file} is not formatted correctly"
            )
        if _DEFAULT_KEY not in Environment.__config:
            raise Exception(
                f"{Environment.__environments_file} does not have a '{_DEFAULT_KEY}'"
            )
        if _ENVIRONMENTS_KEY not in Environment.__config:
            raise Exception(
                f"{Environment.__environments_file} does not have a '{_ENVIRONMENTS_KEY}' section"
            )

        # Get the required environment.
        # First, use anything passed in. If no name is provided
        # use the default value in the file
        if name:
            Environment.__environment = name
        else:
            Environment.__environment = Environment.__config[_DEFAULT_KEY]
        if not Environment.__environment in Environment.__config[_ENVIRONMENTS_KEY]:
            raise Exception(
                f"{Environment.__environments_file} '{Environment.__environment}'"
                " environment does not exist"
            )

        # Get the required key values...
        # We assert if these cannot be found.
        Environment.__keycloak_hostname = str(
            Environment.__get_config_value(_KEYCLOAK_HOSTNAME_KEY)
        )
        Environment.__keycloak_realm = str(
            Environment.__get_config_value(_KEYCLOAK_REALM_KEY)
        )
        Environment.__keycloak_dm_client_id = str(
            Environment.__get_config_value(_KEYCLOAK_DM_CLIENT_ID_KEY)
        )
        Environment.__dm_hostname = str(
            Environment.__get_config_value(_DM_HOSTNAME_KEY)
        )
        Environment.__admin_user = str(Environment.__get_config_value(_ADMIN_USER_KEY))
        Environment.__admin_password = str(
            Environment.__get_config_value(_ADMIN_PASSWORD_KEY)
        )

        # Get the optional key values...
        Environment.__keycloak_as_client_id = Environment.__get_config_value(
            _KEYCLOAK_AS_CLIENT_ID_KEY, optional=True
        )
        Environment.__as_hostname = Environment.__get_config_value(
            _AS_HOSTNAME_KEY, optional=True
        )

    @classmethod
    def __get_config_value(cls, key: str, optional: bool = False) -> Optional[str]:
        """Gets the configuration key's value for the configured environment.
        If optional is False we assert if a value cannot be found or
        return None if it cannot be found and is considered optional.
        """
        assert Environment.__environment
        if (
            not optional
            and key
            not in Environment.__config[_ENVIRONMENTS_KEY][Environment.__environment]
        ):
            raise Exception(
                f"{Environment.__environments_file} '{Environment.__environment}'"
                f" environment does not have a value for '{key}'"
            )
        value: Any = Environment.__config[_ENVIRONMENTS_KEY][
            Environment.__environment
        ].get(key)
        if not value:
            return None
        return str(value)

    @classmethod
    def environment(cls) -> str:
        """Return the environment name."""
        return Environment.__environment

    @classmethod
    def keycloak_hostname(cls) -> str:
        """Return the keycloak hostname. This is the unmodified
        value found in the environment.
        """
        return Environment.__keycloak_hostname

    @classmethod
    def keycloak_url(cls) -> str:
        """Return the keycloak URL. This is the hostname
        plus the 'http' prefix and '/auth' postfix.
        """
        if not Environment.__keycloak_hostname.startswith("http"):
            ret_val: str = f"https://{Environment.__keycloak_hostname}"
        else:
            ret_val = Environment.__keycloak_hostname
        if not ret_val.endswith("/auth"):
            ret_val += "/auth"
        return ret_val

    @classmethod
    def keycloak_realm(cls) -> str:
        """Return the keycloak realm."""
        return Environment.__keycloak_realm

    @classmethod
    def keycloak_as_client_id(cls) -> Optional[str]:
        """Return the keycloak Account Server client ID."""
        return Environment.__keycloak_as_client_id

    @classmethod
    def keycloak_dm_client_id(cls) -> str:
        """Return the keycloak Data Manager client ID."""
        return Environment.__keycloak_dm_client_id

    @classmethod
    def admin_user(cls) -> str:
        """Return the keycloak username."""
        return Environment.__admin_user

    @classmethod
    def admin_password(cls) -> str:
        """Return the keycloak user's password."""
        return Environment.__admin_password

    @classmethod
    def as_hostname(cls) -> Optional[str]:
        """Return the keycloak hostname. This is the unmodified
        value found in the environment but can be None
        """
        return Environment.__as_hostname

    @classmethod
    def as_api(cls) -> Optional[str]:
        """Return the AS API. This is the environment hostname
        with a 'http' prefix and '/account-server-api' postfix.
        """
        if not Environment.__as_hostname:
            return None
        if not Environment.__as_hostname.startswith("http"):
            ret_val: str = f"https://{Environment.__as_hostname}"
        else:
            ret_val = Environment.__as_hostname
        if not ret_val.endswith("/account-server-api"):
            ret_val += "/account-server-api"
        return ret_val

    @classmethod
    def dm_hostname(cls) -> str:
        """Return the keycloak hostname. This is the unmodified
        value found in the environment.
        """
        return Environment.__dm_hostname

    @classmethod
    def dm_api(cls) -> str:
        """Return the DM API. This is the environment hostname
        with a 'http' prefix and '/data-manager-api' postfix.
        """
        if not Environment.__dm_hostname.startswith("http"):
            ret_val: str = f"https://{Environment.__dm_hostname}"
        else:
            ret_val = Environment.__dm_hostname
        if not ret_val.endswith("/data-manager-api"):
            ret_val += "/data-manager-api"
        return ret_val
