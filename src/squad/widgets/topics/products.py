"""A widget used to display AS Product information.
"""
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Tuple

import humanize
import pandas
from rich.panel import Panel
from rich.text import Text
from rich.style import Style

from squonk2.as_api import AsApi

from squad import common
from squad.access_token import AccessToken
from .base import SortOrder, TopicRenderer

# List of columns using names, styles and justification
_COLUMNS: List[Tuple[str, Style, str]] = [
    ("UUID", common.UUID_STYLE, "left"),
    ("Type", common.PRODUCT_TYPE_STYLE, "left"),
    ("Unit", common.NAME_STYLE, "left"),
    ("Name", common.NAME_STYLE, "left"),
    ("Storage", common.STORAGE_SIZE_STYLE, "right"),
    ("Coins", common.COIN_STYLE, "right"),
    ("Allowance", common.COIN_STYLE, "right"),
    ("Limit", common.COIN_STYLE, "right"),
]


class Products(TopicRenderer):
    """Displays AS Products."""

    def __init__(self) -> None:
        # Default sort column
        self.num_columns = len(_COLUMNS)
        self.sort_column = 5

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
            else:
                self.last_response = None

        # Results in a table.
        self.prepare_table(_COLUMNS)
        assert self.table

        # Populate rows based on the last response.
        # We populate 'data' with the project material
        # so that we can sort on 'launched' date using pandas.
        data: Dict[str, List[Any]] = {}
        row_number: int = 1
        if self.last_response and self.last_response.success:
            for product in self.last_response.msg["products"]:
                # A size (or blank)?
                if product["storage"]["size"]["current"] == "0 Bytes":
                    size: str = ""
                else:
                    size = product["storage"]["size"]["current"]
                data[f"{row_number}"] = [
                    product["product"]["id"],
                    product["product"]["type"],
                    product["unit"]["name"],
                    product["product"]["name"],
                    size,
                    Decimal(product["coins"]["used"]),
                    Decimal(product["coins"]["allowance"]),
                    Decimal(product["coins"]["limit"]),
                ]
                row_number += 1

        # Populate rows based on the last response.
        if data:
            data_frame: pandas.DataFrame = pandas.DataFrame.from_dict(
                data, orient="index"
            )
            for _, row in data_frame.sort_values(
                by=[self.sort_column], ascending=self.sort_order == SortOrder.ASCENDING
            ).iterrows():
                coins_used: Decimal = Decimal(format(row[5], ".1f"))
                allowance: Decimal = Decimal(format(row[6], ".1f"))
                limit: Decimal = Decimal(format(row[7], ".1f"))
                coins_used_style: Style = common.COIN_STYLE
                if coins_used > limit:
                    coins_used_style = common.COIN_OVER_LIMIT_STYLE
                elif coins_used > allowance:
                    coins_used_style = common.COIN_OVER_ALLOWANCE_STYLE

                # Coins (if greater than zero)
                if coins_used > Decimal(0):
                    coins: Text = Text(
                        humanize.intcomma(coins_used),
                        style=coins_used_style,
                    )
                else:
                    coins = Text("")

                self.table.add_row(
                    str(self.table.row_count + 1),
                    row[0],
                    row[1],
                    common.truncate(row[2], 15),
                    common.truncate(row[3], 15),
                    row[4],
                    coins,
                    humanize.intcomma(allowance),
                    humanize.intcomma(limit),
                )

        title: str = f"Products ({self.table.row_count})"
        return Panel(
            self.table if self.table.row_count else Text(),
            title=title,
            style=common.CORE_STYLE,
            padding=0,
        )
