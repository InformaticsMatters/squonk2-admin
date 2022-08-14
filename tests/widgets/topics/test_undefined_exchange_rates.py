import pytest

pytestmark = pytest.mark.unit

from rich.panel import Panel

from squad.widgets.topics.base import TopicRenderer
from squad.widgets.topics.undefined_exchange_rates import UndefinedExchangeRates


def test_instantiate():
    # Arrange

    # Act
    tr = UndefinedExchangeRates()

    # Assert
    assert tr is not None
    assert isinstance(tr, UndefinedExchangeRates)
    assert isinstance(tr, TopicRenderer)


def test_render():
    # Arrange
    tr = UndefinedExchangeRates()

    # Act
    panel = tr.render()

    # Assert
    assert panel is not None
    assert isinstance(panel, Panel)
