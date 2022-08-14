import pytest

pytestmark = pytest.mark.unit

from rich.panel import Panel

from squad.widgets.topics.base import TopicRenderer
from squad.widgets.topics.datasets import Datasets


def test_instantiate():
    # Arrange

    # Act
    tr = Datasets()

    # Assert
    assert tr is not None
    assert isinstance(tr, Datasets)
    assert isinstance(tr, TopicRenderer)


def test_render():
    # Arrange
    tr = Datasets()

    # Act
    panel = tr.render()

    # Assert
    assert panel is not None
    assert isinstance(panel, Panel)
