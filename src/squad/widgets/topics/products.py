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
    ("Flavour", common.PRODUCT_FLAVOUR_STYLE, "left"),
    ("Unit", common.NAME_STYLE, "left"),
    ("Name", common.NAME_STYLE, "left"),
    ("On", common.COIN_DAY_STYLE, "right"),
    ("In", common.COIN_RESET_STYLE, "right"),
    ("Storage", common.STORAGE_SIZE_STYLE, "right"),
    ("Claim", common.NAME_STYLE, "left"),
    ("Burn", common.COIN_STYLE, "right"),
    ("Coins", common.COIN_STYLE, "right"),
    ("Prediction", common.COIN_STYLE, "right"),
    ("Allowance", common.COIN_STYLE, "right"),
    ("Limit", common.COIN_STYLE, "right"),
]


class Products(TopicRenderer):
    """Displays AS Products."""

    def __init__(self) -> None:
        # Default sort column
        self.num_columns = len(_COLUMNS)
        self.sort_column = 11

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
                # A claim?
                p_claim: str = ""
                if "claim" in product and "name" in product["claim"]:
                    p_claim = product["claim"]["name"]
                # A size (or blank)?
                if product["storage"]["size"]["current"] == "0 Bytes":
                    size: str = ""
                else:
                    size = product["storage"]["size"]["current"]
                flavour = ""
                if "flavour" in product["product"]:
                    flavour = product["product"]["flavour"]
                data[f"{row_number}"] = [
                    product["product"]["id"],
                    product["product"]["type"],
                    flavour,
                    product["unit"]["name"],
                    product["product"]["name"],
                    humanize.ordinal(product["coins"]["billing_day"]),
                    product["coins"]["remaining_days"],
                    size,
                    p_claim,
                    Decimal(product["coins"]["current_burn_rate"]),
                    Decimal(product["coins"]["used"]),
                    Decimal(product["coins"]["billing_prediction"]),
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

                if row[8]:
                    claim: Text = Text(common.truncate(row[8], common.NAME_LENGTH))
                else:
                    claim = common.CROSS

                # Get data back out of the frame,
                # realising that pandas wil have all sorts of floating point
                # precision issues!
                burn: Decimal = Decimal(format(row[9], ".1f"))
                coins_used: Decimal = Decimal(format(row[10], ".1f"))
                prediction: Decimal = Decimal(format(row[11], ".1f"))
                allowance: Decimal = Decimal(format(row[12], ".1f"))
                limit: Decimal = Decimal(format(row[13], ".1f"))

                coins_used_style: Style = common.COIN_STYLE
                if coins_used > limit:
                    coins_used_style = common.COIN_OVER_LIMIT_STYLE
                elif coins_used > allowance:
                    coins_used_style = common.COIN_OVER_ALLOWANCE_STYLE
                prediction_style: Style = common.COIN_STYLE
                if prediction > limit:
                    prediction_style = common.COIN_OVER_LIMIT_STYLE
                elif prediction > allowance:
                    prediction_style = common.COIN_OVER_ALLOWANCE_STYLE

                # Burn-Rate Coins (if greater than zero)
                # Blank otherwise
                if burn > Decimal(0):
                    burn_coins: Text = Text(
                        humanize.intcomma(burn),
                    )
                else:
                    burn_coins = Text("")

                # Coins (if greater than zero)
                # Blank otherwise
                if coins_used > Decimal(0):
                    coins: Text = Text(
                        humanize.intcomma(coins_used),
                        style=coins_used_style,
                    )
                else:
                    coins = Text("")

                # Prediction Coins (if greater than zero)
                # Blank otherwise
                if prediction > Decimal(0):
                    prediction_coins: Text = Text(
                        humanize.intcomma(prediction),
                        style=prediction_style,
                    )
                else:
                    prediction_coins = Text("")

                self.table.add_row(
                    str(self.table.row_count + 1),
                    row[0],
                    row[1],
                    row[2],
                    common.truncate(row[3], common.NAME_LENGTH),
                    common.truncate(row[4], common.NAME_LENGTH),
                    str(row[5]),
                    str(row[6]),
                    row[7],
                    claim,
                    burn_coins,
                    coins,
                    prediction_coins,
                    humanize.intcomma(allowance),
                    humanize.intcomma(limit),
                )

        title: str = f"Products ({self.table.row_count})"
        return Panel(
            self.table,
            title=title,
            padding=0,
        )
