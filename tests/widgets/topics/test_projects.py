import pytest

pytestmark = pytest.mark.unit

from rich.panel import Panel

from squad.widgets.topics.base import TopicRenderer
from squad.widgets.topics.projects import Projects


def test_instantiate():
    # Arrange

    # Act
    tr = Projects()

    # Assert
    assert tr is not None
    assert isinstance(tr, Projects)
    assert isinstance(tr, TopicRenderer)


def test_render():
    # Arrange
    tr = Projects()

    # Act
    panel = tr.render()

    # Assert
    assert panel is not None
    assert isinstance(panel, Panel)
