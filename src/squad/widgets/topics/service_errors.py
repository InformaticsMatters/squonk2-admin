"""A textual widget used to display DM Service Errors.
"""
from datetime import datetime

from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from squonk2.dm_api import DmApi

from squad import common
from squad.access_token import AccessToken
from .base import TopicRenderer


class ServiceErrors(TopicRenderer):
    """Displays service errors."""

    def render(self) -> Panel:
        """Render the widget."""

        # Time to get exchange rates?
        now = datetime.now()
        if (
            self.last_response_time is None
            or now - self.last_response_time > self.refresh_interval
        ):
            # No response, or we now need to replace what we have.
            # Get an access token (it may be the one we already have)
            self.access_token = AccessToken().get_dm_access_token(
                prior_token=self.access_token
            )
            self.last_response_time = now
            if self.access_token:
                # Got a token, time to get a new set of results.
                self.last_response = DmApi.get_service_errors(self.access_token)

        # Results are presented in a table.
        table: Table = Table(
            collapse_padding=True,
            header_style=common.INDEX_STYLE,
            box=None,
        )
        table.add_column("", style=common.INDEX_STYLE, no_wrap=True, justify="right")
        table.add_column("ID", style=common.ITEM_KEY_STYLE, no_wrap=True)
        table.add_column("Time", style=common.ITEM_KEY_STYLE, no_wrap=True)
        table.add_column("Severity", style=common.ITEM_KEY_STYLE, no_wrap=True)
        table.add_column("Summary", style=common.SIZE_STYLE, no_wrap=True)

        # Populate rows based on the last response.
        if self.last_response and self.last_response.success:
            for error in self.last_response.msg["service_errors"]:
                table.add_row(
                    str(table.row_count + 1),
                    str(error["id"]),
                    error["created"],
                    error["severity"],
                    error["summary"],
                )

        title: str = f"Service errors ({table.row_count})"
        return Panel(
            table if table.row_count else Text(),
            title=title,
            style=common.CORE_STYLE,
            padding=0,
        )
