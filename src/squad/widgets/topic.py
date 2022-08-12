"""A textual widget used to display whatever the user has chosen.
It a dynamic panel that displays Instances, Projects, Datasets etc.
depending on what key the user has hit.
"""
from typing import Dict

from rich.panel import Panel
from textual.widget import Widget

from squad.common import log_warning
from squad.widgets.topics.base import TopicRenderer
from squad.widgets.topics.assets import Assets
from squad.widgets.topics.datasets import Datasets
from squad.widgets.topics.defined_exchange_rates import DefinedExchangeRates
from squad.widgets.topics.instances import Instances
from squad.widgets.topics.merchants import Merchants
from squad.widgets.topics.products import Products
from squad.widgets.topics.projects import Projects
from squad.widgets.topics.personal_units import PersonalUnits
from squad.widgets.topics.service_errors import ServiceErrors
from squad.widgets.topics.undefined_exchange_rates import UndefinedExchangeRates
from squad.widgets.topics.units import Units


class TopicWidget(Widget):  # type: ignore
    """Displays whatever the user has chosen (default is DM Projects)."""

    # What are we displaying?
    topic: str = "instances"
    # What can we display?
    topic_renderers: Dict[str, TopicRenderer] = {
        "assets": Assets(),
        "datasets": Datasets(),
        "defined-exchange-rates": DefinedExchangeRates(),
        "instances": Instances(),
        "merchants": Merchants(),
        "products": Products(),
        "projects": Projects(),
        "personal-units": PersonalUnits(),
        "service-errors": ServiceErrors(),
        "undefined-exchange-rates": UndefinedExchangeRates(),
        "units": Units(),
    }

    @classmethod
    def set_topic(cls, topic: str) -> None:
        """Sets the new topic to display.
        Ignoring topics that are not in the topic_renderers map.
        """
        if topic not in TopicWidget.topic_renderers:
            log_warning(f"Unsupported topic: '{topic}'")
            return
        TopicWidget.topic = topic

    def on_mount(self) -> None:
        """Widget initialisation."""
        # Period between refresh attempts
        # The AS/DM API isn't called at this rate - this is just the
        # rate the chosen info panel is refreshed - each panel decides how often
        # to call the underlying AS or DM (typically every 20 seconds or so).
        self.set_interval(2, self.refresh)

    def render(self) -> Panel:
        """Render the widget using the prevailing topic."""

        assert TopicWidget.topic in TopicWidget.topic_renderers
        return TopicWidget.topic_renderers[TopicWidget.topic].render()
