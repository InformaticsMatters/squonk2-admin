import pytest

pytestmark = pytest.mark.unit

from rich.panel import Panel

from squad.widgets.info import InfoWidget


def test_instantiate_widget():
    # Arrange

    # Act
    widget = InfoWidget()

    # Assert
    assert widget is not None
    assert isinstance(widget, InfoWidget)


def test_render_widget():
    # Arrange
    widget = InfoWidget()

    # Act
    panel = widget.render()

    # Assert
    assert panel is not None
    assert isinstance(panel, Panel)
