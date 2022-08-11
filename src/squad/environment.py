"""Environment module, reads the environment file exposing the values.
"""
# pylint: disable=attribute-defined-outside-init
import os

from yaml import FullLoader, load

from squad.singleton import Singleton

# The environments file (YAML) is typically expected in the user's '~/.squad'
# directory. It contains 'environments' that define the connection details
# for the various Keycloak, Data Manager and Account Server services.
#
# See the project's 'environments' file for an example.
_ENVIRONMENT_DIRECTORY: str = "~/.squad"
_ENVIRONMENT_FILE: str = os.environ.get(
    "SQUAD_ENVIRONMENT_FILE", f"{_ENVIRONMENT_DIRECTORY}/environments"
)

# The key for the block of environments
_ENVIRONMENTS_KEY: str = "environments"
# The 'current' environment
_ENVIRONMENT_KEY: str = "environment"

# Keys required in each environment.
_KEYCLOAK_HOSTNAME_KEY: str = "keycloak-hostname"
_KEYCLOAK_REALM_KEY: str = "keycloak-realm"
_KEYCLOAK_AS_CLIENT_ID_KEY: str = "keycloak-as-client-id"
_KEYCLOAK_DM_CLIENT_ID_KEY: str = "keycloak-dm-client-id"
_AS_HOSTNAME_KEY: str = "as-hostname"
_DM_HOSTNAME_KEY: str = "dm-hostname"
_USER_KEY: str = "user"
_USER_PASSWORD_KEY: str = "password"


class Environment(Singleton):  # type: ignore
    """Loads the environment from the environment file."""

    def init(self, *args, **kwds):
        # type: (*str, **str) -> None
        """Initialisation - loads the environment file,
        returning values form the environment that's named in the file.
        """
        del args
        del kwds

        # Regardless, if there is no default environment directory, create one.
        os.makedirs(os.path.expanduser("~/.squad"), exist_ok=True)

        self.__environments_file: str = os.path.expandvars(
            os.path.expanduser(_ENVIRONMENT_FILE)
        )
        if not os.path.exists(self.__environments_file):
            raise Exception(f"{self.__environments_file} does not exist")
        with open(self.__environments_file, encoding="utf8") as config_file:
            self.__config = load(config_file, Loader=FullLoader)
        # Does it look like YAML?
        if not self.__config:
            raise Exception(f"{self.__environments_file} is empty")
        if not isinstance(self.__config, dict):
            raise Exception(f"{self.__environments_file} is not formatted correctly")
        if _ENVIRONMENT_KEY not in self.__config:
            raise Exception(
                f"{self.__environments_file} does not have a '{_ENVIRONMENT_KEY}'"
            )
        if _ENVIRONMENTS_KEY not in self.__config:
            raise Exception(
                f"{self.__environments_file} does not have a '{_ENVIRONMENTS_KEY}' section"
            )
        # Get (current) environment
        self.__environment: str = self.__config[_ENVIRONMENT_KEY]
        if not self.__environment in self.__config[_ENVIRONMENTS_KEY]:
            raise Exception(
                f"{self.__environments_file} '{self.__environment}' environment does not exist"
            )
        # Get the required key values...
        self.__keycloak_hostname: str = self.__get_config_value(_KEYCLOAK_HOSTNAME_KEY)
        self.__keycloak_realm: str = self.__get_config_value(_KEYCLOAK_REALM_KEY)
        self.__keycloak_as_client_id: str = self.__get_config_value(
            _KEYCLOAK_AS_CLIENT_ID_KEY
        )
        self.__keycloak_dm_client_id: str = self.__get_config_value(
            _KEYCLOAK_DM_CLIENT_ID_KEY
        )
        self.__as_hostname: str = self.__get_config_value(_AS_HOSTNAME_KEY)
        self.__dm_hostname: str = self.__get_config_value(_DM_HOSTNAME_KEY)
        self.__user: str = self.__get_config_value(_USER_KEY)
        self.__user_password: str = self.__get_config_value(_USER_PASSWORD_KEY)

    def __get_config_value(self, key: str) -> str:
        """Gets the configuration key's value for the configured environment."""
        assert self.__environment
        if key not in self.__config[_ENVIRONMENTS_KEY][self.__environment]:
            raise Exception(
                f"{self.__environments_file} '{self.__environment}'"
                f" environment does not have a value for '{key}'"
            )
        return str(self.__config[_ENVIRONMENTS_KEY][self.__environment][key])

    def environment(self) -> str:
        """Return the environment name."""
        return self.__environment

    def keycloak_hostname(self) -> str:
        """Return the keycloak hostname. This is the unmodified
        value found in the environment.
        """
        return self.__keycloak_hostname

    def keycloak_url(self) -> str:
        """Return the keycloak URL. This is the hostname
        plus the 'http' prefix and '/auth' postfix.
        """
        if not self.__keycloak_hostname.startswith("http"):
            ret_val: str = f"https://{self.__keycloak_hostname}"
        else:
            ret_val = self.__keycloak_hostname
        if not ret_val.endswith("/auth"):
            ret_val += "/auth"
        return ret_val

    def keycloak_realm(self) -> str:
        """Return the keycloak realm."""
        return self.__keycloak_realm

    def keycloak_as_client_id(self) -> str:
        """Return the keycloak Account Server client ID."""
        return self.__keycloak_as_client_id

    def keycloak_dm_client_id(self) -> str:
        """Return the keycloak Data Manager client ID."""
        return self.__keycloak_dm_client_id

    def user(self) -> str:
        """Return the keycloak username."""
        return self.__user

    def user_password(self) -> str:
        """Return the keycloak user's password."""
        return self.__user_password

    def as_api(self) -> str:
        """Return the AS API. This is the environment hostname
        with a 'http' prefix and '/account-server-api' postfix.
        """
        if not self.__as_hostname.startswith("http"):
            ret_val: str = f"https://{self.__as_hostname}"
        else:
            ret_val = self.__as_hostname
        if not ret_val.endswith("/account-server-api"):
            ret_val += "/account-server-api"
        return ret_val

    def dm_api(self) -> str:
        """Return the DM API. This is the environment hostname
        with a 'http' prefix and '/data-manager-api' postfix.
        """
        if not self.__dm_hostname.startswith("http"):
            ret_val: str = f"https://{self.__dm_hostname}"
        else:
            ret_val = self.__dm_hostname
        if not ret_val.endswith("/data-manager-api"):
            ret_val += "/data-manager-api"
        return ret_val
