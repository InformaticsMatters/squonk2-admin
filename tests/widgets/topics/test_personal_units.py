import pytest

pytestmark = pytest.mark.unit

from rich.panel import Panel

from squad.widgets.topics.base import TopicRenderer
from squad.widgets.topics.personal_units import PersonalUnits


def test_instantiate():
    # Arrange

    # Act
    tr = PersonalUnits()

    # Assert
    assert tr is not None
    assert isinstance(tr, PersonalUnits)
    assert isinstance(tr, TopicRenderer)


def test_render():
    # Arrange
    tr = PersonalUnits()

    # Act
    panel = tr.render()

    # Assert
    assert panel is not None
    assert isinstance(panel, Panel)
