"""A widget used to display DM Project information.
"""
from datetime import datetime
from typing import Any, Dict, List, Tuple

import humanize
import pandas
from rich.panel import Panel
from rich.style import Style

from squonk2.dm_api import DmApi

from squad import common
from squad.access_token import AccessToken
from .base import SortOrder, TopicRenderer

# List of columns using names, styles and justification (centred by default)
_COLUMNS: List[Tuple[str, Style, str]] = [
    ("UUID", common.UUID_STYLE, "left"),
    ("Name", common.NAME_STYLE, "left"),
    ("Owner", common.USER_STYLE, "left"),
    ("Size", common.STORAGE_SIZE_STYLE, "right"),
]


class Projects(TopicRenderer):
    """Displays projects."""

    def __init__(self) -> None:
        # Default sort column
        self.num_columns = 4
        self.sort_column = 3

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
            self.access_token = AccessToken.get_dm_access_token(
                prior_token=self.access_token
            )
            self.last_response_time = now
            if self.access_token:
                # Got a token, time to get a new set of results...
                self.last_response = DmApi.get_available_projects(self.access_token)
            else:
                self.last_response = None

        # Results in a table.
        self.prepare_table(_COLUMNS)
        assert self.table

        # Populate rows based on the last response.
        # We populate 'data' with the project material
        # so that we can sort of size using pandas.
        data: Dict[str, List[Any]] = {}
        total_size_bytes: int = 0
        row_number: int = 1
        if self.last_response and self.last_response.success:
            for project in self.last_response.msg["projects"]:
                total_size_bytes += project["size"]
                data[f"{row_number}"] = [
                    project["project_id"],
                    project["name"],
                    project["owner"],
                    project["size"],
                ]
                row_number += 1

        # Now sort the data by size (descending)
        # and then iterate through the results.
        if data:
            data_frame: pandas.DataFrame = pandas.DataFrame.from_dict(
                data, orient="index"
            )
            for _, row in data_frame.sort_values(
                by=[self.sort_column], ascending=self.sort_order == SortOrder.ASCENDING
            ).iterrows():
                size_str: str = ""
                if row[3] > 0:
                    size_str = humanize.naturalsize(row[3], binary=True)
                self.table.add_row(
                    str(self.table.row_count + 1),
                    row[0],
                    common.truncate(row[1], common.NAME_LENGTH),
                    row[2],
                    size_str,
                )

        total_size_human: str = humanize.naturalsize(total_size_bytes, binary=True)
        title: str = f"Projects ({self.table.row_count}) [{total_size_human}]"
        return Panel(
            self.table,
            title=title,
        )
