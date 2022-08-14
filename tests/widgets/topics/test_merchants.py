import pytest

pytestmark = pytest.mark.unit

from rich.panel import Panel

from squad.widgets.topics.base import TopicRenderer
from squad.widgets.topics.merchants import Merchants


def test_instantiate():
    # Arrange

    # Act
    tr = Merchants()

    # Assert
    assert tr is not None
    assert isinstance(tr, Merchants)
    assert isinstance(tr, TopicRenderer)


def test_render():
    # Arrange
    tr = Merchants()

    # Act
    panel = tr.render()

    # Assert
    assert panel is not None
    assert isinstance(panel, Panel)
