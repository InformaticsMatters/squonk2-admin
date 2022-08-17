"""A widget used to display AS Asset information.
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

# List of columns using names, styles and justification
_COLUMNS: List[Tuple[str, Style, str]] = [
    ("Name", common.NAME_STYLE, "left"),
    ("Creator", common.USER_STYLE, "left"),
    ("Scope", None, "left"),
    ("Scope ID", None, "left"),
    ("Created (UTC)", common.DATE_STYLE, "left"),
    ("Disabled", None, "centre"),
    ("Secret", None, "centre"),
    ("Merchants", common.MERCHANT_NAME_STYLE, "left"),
]

# Local dictionary of styles for Asset 'scopes'.
_SCOPE_STYLE: Dict[str, Style] = {
    "USER": Style(color="yellow1"),
    "PRODUCT": Style(color="green_yellow"),
    "UNIT": Style(color="pale_turquoise1"),
    "ORGANISATION": Style(color="violet"),
}
_DEFAULT_SCOPE_STYLE: Style = Style(color="light_sky_blue1")


class Assets(TopicRenderer):
    """Displays AS assets."""

    def __init__(self) -> None:
        # Default sort column
        self.num_columns = len(_COLUMNS)
        self.sort_column = 4

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
            for asset in self.last_response.msg["assets"]:
                # Comma-separated list of merchants
                merchants: str = ""
                for merchant in asset["merchants"]:
                    merchants += merchant["name"] + ","
                # Strip off the trailing comma.
                if merchants:
                    merchants = merchants[:-1]
                data[f"{row_number}"] = [
                    asset["name"],
                    asset["creator"],
                    asset["scope"],
                    asset["scope_id"],
                    asset["created"],
                    asset["disabled"],
                    asset["secret"],
                    merchants,
                ]
                row_number += 1

        if data:
            data_frame: pandas.DataFrame = pandas.DataFrame.from_dict(
                data, orient="index"
            )
            for _, row in data_frame.sort_values(
                by=[self.sort_column], ascending=self.sort_order == SortOrder.ASCENDING
            ).iterrows():
                # The scope (user/unit etc.)
                scope: str = row[2]
                self.table.add_row(
                    str(self.table.row_count + 1),
                    common.truncate(row[0], common.NAME_LENGTH),
                    row[1],
                    Text(
                        scope,
                        style=_SCOPE_STYLE.get(scope, _DEFAULT_SCOPE_STYLE),
                    ),
                    Text(
                        row[3],
                        style=_SCOPE_STYLE.get(scope, _DEFAULT_SCOPE_STYLE),
                    ),
                    row[4],
                    common.TICK if row[5] else common.CROSS,
                    common.TICK if row[6] else common.CROSS,
                    row[7],
                )

        title: str = f"Assets ({self.table.row_count})"
        return Panel(
            self.table,
            title=title,
        )
