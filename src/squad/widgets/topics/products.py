"""A widget used to display AS Product information.
"""
from datetime import datetime
from decimal import Decimal

import humanize
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.style import Style

from squonk2.as_api import AsApi

from squad import common
from squad.access_token import AccessToken
from .base import TopicRenderer


class Products(TopicRenderer):
    """Displays AS Products."""

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
                self.last_response = AsApi.get_available_products(self.access_token)

        # Results in a table.
        table: Table = Table(
            collapse_padding=True,
            header_style=common.INDEX_STYLE,
            box=None,
        )
        table.add_column("", style=common.INDEX_STYLE, no_wrap=True, justify="right")
        table.add_column("UUID", style=common.ITEM_KEY_STYLE, no_wrap=True)
        table.add_column("Type", style=common.TYPE_STYLE, no_wrap=True)
        table.add_column("Unit", style=common.NAME_STYLE, no_wrap=True)
        table.add_column("Name", style=common.NAME_STYLE, no_wrap=True)
        table.add_column(
            "Storage", style=common.SIZE_STYLE, no_wrap=True, justify="right"
        )
        table.add_column(
            "Coins", style=common.COIN_STYLE, no_wrap=True, justify="right"
        )
        table.add_column(
            "Allowance", style=common.COIN_STYLE, no_wrap=True, justify="right"
        )
        table.add_column(
            "Limit", style=common.COIN_STYLE, no_wrap=True, justify="right"
        )

        # Populate rows based on the last response.
        if self.last_response and self.last_response.success:
            for product in self.last_response.msg["products"]:
                coins_used: Decimal = Decimal(product["coins"]["used"])
                allowance: Decimal = Decimal(product["coins"]["allowance"])
                limit: Decimal = Decimal(product["coins"]["limit"])
                coins_used_style: Style = common.COIN_STYLE
                if coins_used > limit:
                    coins_used_style = common.COIN_LIMIT_STYLE
                elif coins_used > allowance:
                    coins_used_style = common.COIN_OVERSPEND_STYLE

                # A size (or blank)?
                if product["storage"]["size"]["current"] == "0 Bytes":
                    size: str = ""
                else:
                    size = product["storage"]["size"]["current"]

                # Coins (if greater than zero)
                if coins_used > Decimal(0):
                    coins: Text = Text(
                        humanize.intcomma(product["coins"]["used"]),
                        style=coins_used_style,
                    )
                else:
                    coins = Text("")

                table.add_row(
                    str(table.row_count + 1),
                    product["product"]["id"],
                    product["product"]["type"],
                    product["unit"]["name"],
                    product["product"]["name"],
                    size,
                    coins,
                    humanize.intcomma(product["coins"]["allowance"]),
                    humanize.intcomma(product["coins"]["limit"]),
                )

        title: str = f"Products ({table.row_count})"
        return Panel(
            table if table.row_count else Text(),
            title=title,
            style=common.CORE_STYLE,
            padding=0,
        )
