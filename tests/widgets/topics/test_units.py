import pytest

pytestmark = pytest.mark.unit

from rich.panel import Panel

from squad.widgets.topics.base import TopicRenderer
from squad.widgets.topics.units import Units


def test_instantiate():
    # Arrange

    # Act
    tr = Units()

    # Assert
    assert tr is not None
    assert isinstance(tr, Units)
    assert isinstance(tr, TopicRenderer)


def test_render():
    # Arrange
    tr = Units()

    # Act
    panel = tr.render()

    # Assert
    assert panel is not None
    assert isinstance(panel, Panel)
