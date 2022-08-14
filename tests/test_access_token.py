import pytest

pytestmark = pytest.mark.unit

from squad.access_token import AccessToken


def test_as_access_token_without_config():
    # Arrange

    # Act
    result = AccessToken.get_as_access_token()

    # Assert
    assert result is None


def test_dm_access_token_without_config():
    # Arrange

    # Act
    result = AccessToken.get_dm_access_token()

    # Assert
    assert result is None
