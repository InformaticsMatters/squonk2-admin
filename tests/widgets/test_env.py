import pytest

pytestmark = pytest.mark.unit

from rich.panel import Panel

from squad.widgets.env import EnvWidget


def test_instantiate_widget():
    # Arrange

    # Act
    widget = EnvWidget()

    # Assert
    assert widget is not None
    assert isinstance(widget, EnvWidget)


def test_render_widget():
    # Arrange
    widget = EnvWidget()

    # Act
    panel = widget.render()

    # Assert
    assert panel is not None
    assert isinstance(panel, Panel)
