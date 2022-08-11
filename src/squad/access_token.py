"""Gets AS and DM access tokens.
"""
from typing import Optional
from squonk2.auth import Auth

from squad.environment import Environment
from squad.singleton import Singleton


class AccessToken(Singleton):  # type: ignore
    """Gets AS or DM access tokens."""

    def __init__(self) -> None:
        """Get key environment values."""
        environment: Environment = Environment()
        self.kc_url: str = environment.keycloak_url()
        self.kc_realm: str = environment.keycloak_realm()
        self.kc_as_client_id: str = environment.keycloak_as_client_id()
        self.kc_dm_client_id: str = environment.keycloak_dm_client_id()
        self.user: str = environment.user()
        self.password: str = environment.user_password()

    def get_as_access_token(
        self, *, prior_token: Optional[str] = None
    ) -> Optional[str]:
        """Returns a token for the AS API."""
        access_token: Optional[str] = Auth.get_access_token(
            keycloak_url=self.kc_url,
            keycloak_realm=self.kc_realm,
            keycloak_client_id=self.kc_as_client_id,
            username=self.user,
            password=self.password,
            prior_token=prior_token,
        )
        return access_token

    def get_dm_access_token(
        self, *, prior_token: Optional[str] = None
    ) -> Optional[str]:
        """Returns a token for the DM API."""
        access_token: Optional[str] = Auth.get_access_token(
            keycloak_url=self.kc_url,
            keycloak_realm=self.kc_realm,
            keycloak_client_id=self.kc_dm_client_id,
            username=self.user,
            password=self.password,
            prior_token=prior_token,
        )
        return access_token
