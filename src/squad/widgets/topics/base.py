"""The base class for all widgets."""
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Optional, Union

from rich.panel import Panel

from squonk2.as_api import AsApiRv
from squonk2.dm_api import DmApiRv


class TopicRenderer(ABC):
    """The base class for all widgets."""

    access_token: Optional[str] = None

    # Period between calls to the DmApi.
    # We do not call the DmApi more frequently than this.
    refresh_interval: timedelta = timedelta(seconds=20)
    # The last response from the DmApi (or AsApi) in a renderer.
    last_response: Optional[Union[DmApiRv, AsApiRv]] = None
    # The time we got the last response
    last_response_time: Optional[datetime] = None

    @abstractmethod
    def render(self) -> Panel:
        """Render the widget."""
