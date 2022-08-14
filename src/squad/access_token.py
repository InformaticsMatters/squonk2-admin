"""Gets AS and DM access tokens.
"""
from typing import Optional
from squonk2.auth import Auth

from squad.environment import Environment


class AccessToken:
    """Gets AS or DM access tokens."""

    @classmethod
    def get_as_access_token(cls, *, prior_token: Optional[str] = None) -> Optional[str]:
        """Returns a token for the AS API.
        This returns None on error or if the client ID is not defined.
        """
        if not Environment.keycloak_as_client_id():
            return None
        access_token: Optional[str] = Auth.get_access_token(
            keycloak_url=Environment.keycloak_url(),
            keycloak_realm=Environment.keycloak_realm(),
            keycloak_client_id=Environment.keycloak_as_client_id(),
            username=Environment.admin_user(),
            password=Environment.admin_password(),
            prior_token=prior_token,
        )
        return access_token

    @classmethod
    def get_dm_access_token(cls, *, prior_token: Optional[str] = None) -> Optional[str]:
        """Returns a token for the DM API or None if a token could not be obtained."""
        if not Environment.keycloak_dm_client_id():
            return None
        access_token: Optional[str] = Auth.get_access_token(
            keycloak_url=Environment.keycloak_url(),
            keycloak_realm=Environment.keycloak_realm(),
            keycloak_client_id=Environment.keycloak_dm_client_id(),
            username=Environment.admin_user(),
            password=Environment.admin_password(),
            prior_token=prior_token,
        )
        return access_token
