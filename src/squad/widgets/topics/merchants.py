"""A widget used to display AS Merchant information.
"""
from datetime import datetime
from typing import Any, Dict, List, Tuple

import pandas
from rich.panel import Panel
from rich.text import Text
from rich.style import Style
from squonk2.as_api import AsApi

from squad import common
from squad.access_token import AccessToken
from .base import SortOrder, TopicRenderer

# List of columns using names, styles and justification.
# some styles are dynamic.
_COLUMNS: List[Tuple[str, Style, str]] = [
    ("ID", common.MERCHANT_ID_STYLE, "right"),
    ("Kind", None, "left"),
    ("Created (UTC)", common.DATE_STYLE, "left"),
    ("Hostname", common.HOSTNAME_STYLE, "left"),
    ("Name", common.MERCHANT_NAME_STYLE, "left"),
]

# Styles for instance phases.
_MERCHANT_STYLE: Dict[str, Style] = {
    "DATA_MANAGER": Style(color="light_pink1"),
}
_DEFAULT_MERCHANT_STYLE: Style = Style(color="green4")


class Merchants(TopicRenderer):
    """Displays AS assets."""

    def __init__(self) -> None:
        # Default sort column
        self.num_columns = len(_COLUMNS)
        self.sort_column = 1

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
            for merchant in self.last_response.msg["merchants"]:
                data[f"{row_number}"] = [
                    merchant["id"],
                    merchant["kind"],
                    merchant["created"],
                    merchant["api_hostname"],
                    common.truncate(merchant["name"], common.NAME_LENGTH),
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
                kind: str = row[1]
                self.table.add_row(
                    str(self.table.row_count + 1),
                    str(row[0]),
                    Text(
                        kind, style=_MERCHANT_STYLE.get(kind, _DEFAULT_MERCHANT_STYLE)
                    ),
                    row[2],
                    row[3],
                    row[4],
                )

        title: str = f"Merchants ({self.table.row_count})"
        return Panel(
            self.table,
            title=title,
        )
