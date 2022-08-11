"""A widget used to display AS Merchant information.
"""
from datetime import datetime
from typing import Dict

from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.style import Style
from squonk2.as_api import AsApi

from squad import common
from squad.access_token import AccessToken
from .base import TopicRenderer

# Styles for instance phases.
_MERCHANT_STYLE: Dict[str, Style] = {
    "DATA_MANAGER": Style(color="light_pink1"),
}
_DEFAULT_MERCHANT_STYLE: Style = Style(color="green4")


class Merchants(TopicRenderer):
    """Displays AS assets."""

    def render(self) -> Panel:
        """Render the widget."""

        # Time to get projects?
        now = datetime.now()
        if (
            self.last_response_time is None
            or now - self.last_response_time > self.refresh_interval
        ):
            # No response, or we now need to replace what we have.
            # Get an access token (it may be the one we already have)
            self.access_token = AccessToken.get_as_access_token(
                prior_token=self.access_token
            )
            self.last_response_time = now
            if self.access_token:
                # Got a token, time to get a new set of results...
                self.last_response = AsApi.get_merchants(self.access_token)

        # Results in a table.
        table: Table = Table(
            collapse_padding=True,
            header_style=common.INDEX_STYLE,
            box=None,
        )
        table.add_column("", style=common.INDEX_STYLE, no_wrap=True, justify="right")
        table.add_column("ID", no_wrap=True, style=common.USER_STYLE, justify="right")
        table.add_column("Kind", no_wrap=True)
        table.add_column("Created (UTC)", style=common.DATE_STYLE, no_wrap=True)
        table.add_column("Hostname", style=common.ITEM_KEY_STYLE, no_wrap=True)
        table.add_column("Name", style=common.MERCHANT_STYLE, no_wrap=True)

        # Populate rows based on the last response.
        if self.last_response and self.last_response.success:
            for merchant in self.last_response.msg["merchants"]:
                kind: str = merchant["kind"]
                table.add_row(
                    str(table.row_count + 1),
                    str(merchant["id"]),
                    Text(
                        kind, style=_MERCHANT_STYLE.get(kind, _DEFAULT_MERCHANT_STYLE)
                    ),
                    merchant["created"],
                    merchant["api_hostname"],
                    merchant["name"],
                )

        title: str = f"Merchants ({table.row_count})"
        return Panel(
            table if table.row_count else Text(),
            title=title,
            style=common.CORE_STYLE,
            padding=0,
        )
