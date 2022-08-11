"""A widget used to display AS Asset information.
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

# Styles for Asset scopes.
_SCOPE_STYLE: Dict[str, Style] = {
    "USER": Style(color="yellow1"),
    "PRODUCT": Style(color="green_yellow"),
    "UNIT": Style(color="pale_turquoise1"),
    "ORGANISATION": Style(color="violet"),
}
_DEFAULT_SCOPE_STYLE: Style = Style(color="light_sky_blue1")


class Assets(TopicRenderer):
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
                self.last_response = AsApi.get_available_assets(self.access_token)

        # Results in a table.
        table: Table = Table(
            collapse_padding=True,
            header_style=common.INDEX_STYLE,
            box=None,
        )
        table.add_column("", style=common.INDEX_STYLE, no_wrap=True, justify="right")
        table.add_column("Name", style=common.NAME_STYLE, no_wrap=True)
        table.add_column("Creator", style=common.USER_STYLE, no_wrap=True)
        table.add_column("Scope ID", style=common.ITEM_KEY_STYLE, no_wrap=True)
        table.add_column("Created (UTC)", style=common.DATE_STYLE, no_wrap=True)
        table.add_column("Disabled", no_wrap=True, justify="center")
        table.add_column("Secret", no_wrap=True, justify="center")
        table.add_column("Merchants", no_wrap=True, style=common.MERCHANT_STYLE)

        # Populate rows based on the last response.
        if self.last_response and self.last_response.success:
            for asset in self.last_response.msg["assets"]:
                # The scope (user/unit etc.)
                scope: str = asset["scope"]
                # Comma-separated list of merchants
                merchants: str = ""
                for merchant in asset["merchants"]:
                    merchants += merchant["name"] + ","
                # Strip off the trailing comma.
                if merchants:
                    merchants = merchants[:-1]
                table.add_row(
                    str(table.row_count + 1),
                    asset["name"],
                    asset["creator"],
                    Text(
                        asset["scope_id"],
                        style=_SCOPE_STYLE.get(scope, _DEFAULT_SCOPE_STYLE),
                    ),
                    asset["created"],
                    common.TICK if asset["disabled"] else common.CROSS,
                    common.TICK if asset["secret"] else common.CROSS,
                    merchants,
                )

        title: str = f"Assets ({table.row_count})"
        return Panel(
            table if table.row_count else Text(),
            title=title,
            style=common.CORE_STYLE,
            padding=0,
        )
