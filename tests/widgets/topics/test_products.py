import pytest

pytestmark = pytest.mark.unit

from rich.panel import Panel

from squad.widgets.topics.base import TopicRenderer
from squad.widgets.topics.products import Products


def test_instantiate():
    # Arrange

    # Act
    tr = Products()

    # Assert
    assert tr is not None
    assert isinstance(tr, Products)
    assert isinstance(tr, TopicRenderer)


def test_render():
    # Arrange
    tr = Products()

    # Act
    panel = tr.render()

    # Assert
    assert panel is not None
    assert isinstance(panel, Panel)
