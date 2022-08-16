import pytest

pytestmark = pytest.mark.unit

from rich.panel import Panel

from squad.widgets.topics.base import TopicRenderer
from squad.widgets.topics.tasks import Tasks


def test_instantiate():
    # Arrange

    # Act
    tr = Tasks()

    # Assert
    assert tr is not None
    assert isinstance(tr, Tasks)
    assert isinstance(tr, TopicRenderer)


def test_render():
    # Arrange
    tr = Tasks()

    # Act
    panel = tr.render()

    # Assert
    assert panel is not None
    assert isinstance(panel, Panel)
