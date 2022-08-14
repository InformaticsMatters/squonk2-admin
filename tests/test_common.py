import pytest

pytestmark = pytest.mark.unit

from squad import common


def test_truncate_longest():
    # Arrange

    # Act
    result = common.truncate("abcdefgh", 8)

    # Assert
    assert result == "abcdefgh"


def test_truncate_too_long():
    # Arrange

    # Act
    result = common.truncate("abcdefgh", 7)

    # Assert
    assert result == "abcdef" + "\u2026"
