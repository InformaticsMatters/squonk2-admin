import pytest

pytestmark = pytest.mark.unit

from rich.panel import Panel

from squad.widgets.topics.base import TopicRenderer
from squad.widgets.topics.service_errors import ServiceErrors


def test_instantiate():
    # Arrange

    # Act
    tr = ServiceErrors()

    # Assert
    assert tr is not None
    assert isinstance(tr, ServiceErrors)
    assert isinstance(tr, TopicRenderer)


def test_render():
    # Arrange
    tr = ServiceErrors()

    # Act
    panel = tr.render()

    # Assert
    assert panel is not None
    assert isinstance(panel, Panel)
