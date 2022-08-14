import pytest

pytestmark = pytest.mark.unit

from rich.panel import Panel

from squad.widgets.topics.base import TopicRenderer
from squad.widgets.topics.assets import Assets


def test_instantiate():
    # Arrange

    # Act
    tr = Assets()

    # Assert
    assert tr is not None
    assert isinstance(tr, Assets)
    assert isinstance(tr, TopicRenderer)


def test_render():
    # Arrange
    tr = Assets()

    # Act
    panel = tr.render()

    # Assert
    assert panel is not None
    assert isinstance(panel, Panel)
