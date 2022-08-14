import pytest

pytestmark = pytest.mark.unit

from rich.panel import Panel

from squad.widgets.logo import LogoWidget


def test_instantiate_widget():
    # Arrange

    # Act
    widget = LogoWidget()

    # Assert
    assert widget is not None
    assert isinstance(widget, LogoWidget)


def test_render_widget():
    # Arrange
    widget = LogoWidget()

    # Act
    panel = widget.render()

    # Assert
    assert panel is not None
    assert isinstance(panel, Panel)
