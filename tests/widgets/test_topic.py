import pytest

pytestmark = pytest.mark.unit

from rich.panel import Panel

from squad.widgets.topic import TopicWidget


def test_instantiate_widget():
    # Arrange

    # Act
    widget = TopicWidget()

    # Assert
    assert widget is not None
    assert isinstance(widget, TopicWidget)


def test_render_widget():
    # Arrange
    widget = TopicWidget()

    # Act
    panel = widget.render()

    # Assert
    assert panel is not None
    assert isinstance(panel, Panel)
