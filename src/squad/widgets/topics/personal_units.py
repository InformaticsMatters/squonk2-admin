"""A widget used to display AS Personal Units.
"""
from datetime import datetime
from typing import Any, Dict, List, Tuple

import pandas
from rich.panel import Panel
from rich.style import Style

from squonk2.as_api import AsApi

from squad import common
from squad.access_token import AccessToken
from .base import SortOrder, TopicRenderer

# List of columns using names, styles and justification.
# some styles are dynamic.
_COLUMNS: List[Tuple[str, Style, str]] = [
    ("UUID", common.UUID_STYLE, "left"),
    ("Owner", common.USER_STYLE, "left"),
    ("Created (UTC)", common.DATE_STYLE, "left"),
    ("Private", None, "center"),
]


class PersonalUnits(TopicRenderer):
    """Displays AS 'personal' Units,
    units that belong to the 'Default' organisation.
    """

    def __init__(self) -> None:
        # Default sort column
        self.num_columns = len(_COLUMNS)
        self.sort_column = 2

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
            for unit in self.last_response.msg["units"]:
                # Skip units that are not in the Default organisation
                if unit["organisation"]["name"] != "Default":
                    continue
                for org_unit in unit["units"]:
                    data[f"{row_number}"] = [
                        org_unit["id"],
                        org_unit["owner_id"],
                        org_unit["created"],
                        org_unit["private"],
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
                self.table.add_row(
                    str(self.table.row_count + 1),
                    row[0],
                    row[1],
                    row[2],
                    common.TICK if row[3] else common.CROSS,
                )

        title: str = f"Personal units ({self.table.row_count})"
        return Panel(
            self.table,
            title=title,
        )
