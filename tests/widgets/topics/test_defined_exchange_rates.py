import pytest

pytestmark = pytest.mark.unit

from rich.panel import Panel

from squad.widgets.topics.base import TopicRenderer
from squad.widgets.topics.defined_exchange_rates import DefinedExchangeRates


def test_instantiate():
    # Arrange

    # Act
    tr = DefinedExchangeRates()

    # Assert
    assert tr is not None
    assert isinstance(tr, DefinedExchangeRates)
    assert isinstance(tr, TopicRenderer)


def test_render():
    # Arrange
    tr = DefinedExchangeRates()

    # Act
    panel = tr.render()

    # Assert
    assert panel is not None
    assert isinstance(panel, Panel)
