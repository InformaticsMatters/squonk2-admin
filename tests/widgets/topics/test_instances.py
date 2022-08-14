import pytest

pytestmark = pytest.mark.unit

from rich.panel import Panel

from squad.widgets.topics.base import TopicRenderer
from squad.widgets.topics.instances import Instances


def test_instantiate():
    # Arrange

    # Act
    tr = Instances()

    # Assert
    assert tr is not None
    assert isinstance(tr, Instances)
    assert isinstance(tr, TopicRenderer)


def test_render():
    # Arrange
    tr = Instances()

    # Act
    panel = tr.render()

    # Assert
    assert panel is not None
    assert isinstance(panel, Panel)
