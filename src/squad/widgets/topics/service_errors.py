"""A textual widget used to display DM Service Errors.
"""
from datetime import datetime
from typing import Any, Dict, List, Tuple

import pandas
from rich.panel import Panel
from rich.style import Style
from squonk2.dm_api import DmApi

from squad import common
from squad.access_token import AccessToken
from .base import SortOrder, TopicRenderer

# List of columns using names, styles and justification.
# some styles are dynamic.
_COLUMNS: List[Tuple[str, Style, str]] = [
    ("ID", common.UUID_STYLE, "right"),
    ("Time (UTC)", common.DATE_STYLE, "left"),
    ("Severity", None, "left"),
    ("Summary", common.MSG_STYLE, "left"),
]


class ServiceErrors(TopicRenderer):
    """Displays service errors."""

    def __init__(self) -> None:
        # Default sort column
        self.num_columns = len(_COLUMNS)
        self.sort_column = 1

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
            self.access_token = AccessToken.get_dm_access_token(
                prior_token=self.access_token
            )
            self.last_response_time = now
            if self.access_token:
                # Got a token, time to get a new set of results.
                self.last_response = DmApi.get_service_errors(self.access_token)
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
            for error in self.last_response.msg["service_errors"]:
                data[f"{row_number}"] = [
                    error["id"],
                    error["created"],
                    error["severity"],
                    error["summary"],
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
                    str(row[0]),
                    row[1],
                    row[2],
                    row[3],
                )

        title: str = f"Service errors ({self.table.row_count})"
        return Panel(
            self.table,
            title=title,
        )
