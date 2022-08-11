"""A widget used to display AS Unit information.
"""
from datetime import datetime

from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from squonk2.as_api import AsApi

from squad import common
from squad.access_token import AccessToken
from .base import TopicRenderer


class Units(TopicRenderer):
    """Displays AS Units (and their organisations).
    This does not include 'personal units'
    """

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
                self.last_response = AsApi.get_available_units(self.access_token)

        # Results in a table.
        table: Table = Table(
            collapse_padding=True,
            header_style=common.INDEX_STYLE,
            box=None,
        )
        table.add_column("", style=common.INDEX_STYLE, no_wrap=True, justify="right")
        table.add_column("Org", style=common.NAME_STYLE, no_wrap=True)
        table.add_column("UUID", style=common.ITEM_KEY_STYLE, no_wrap=True)
        table.add_column("Name", style=common.NAME_STYLE, no_wrap=True)
        table.add_column("Owner", style=common.USER_STYLE, no_wrap=True)
        table.add_column("Created (UTC)", style=common.DATE_STYLE, no_wrap=True)
        table.add_column("Private", no_wrap=True, justify="center")

        # Populate rows based on the last response.
        if self.last_response and self.last_response.success:
            for unit in self.last_response.msg["units"]:
                unit_org: str = unit["organisation"]["name"]
                # Skip units in the Default organisation
                if unit_org == "Default":
                    continue
                for org_unit in unit["units"]:
                    table.add_row(
                        str(table.row_count + 1),
                        unit_org,
                        org_unit["id"],
                        org_unit["name"],
                        org_unit["owner_id"],
                        org_unit["created"],
                        common.TICK if org_unit["private"] else common.CROSS,
                    )
                    unit_org = ""

        title: str = f"Units ({table.row_count})"
        return Panel(
            table if table.row_count else Text(),
            title=title,
            style=common.CORE_STYLE,
            padding=0,
        )
