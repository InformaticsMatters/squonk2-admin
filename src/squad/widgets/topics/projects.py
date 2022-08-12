"""A widget used to display DM Project information.
"""
from datetime import datetime
from typing import Any, Dict, List

import humanize
import pandas
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from squonk2.dm_api import DmApi

from squad import common
from squad.access_token import AccessToken
from .base import TopicRenderer


class Projects(TopicRenderer):
    """Displays projects."""

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
        table: Table = Table(
            collapse_padding=True,
            header_style=common.INDEX_STYLE,
            box=None,
        )
        table.add_column("", style=common.INDEX_STYLE, no_wrap=True, justify="right")
        table.add_column("UUID", style=common.ITEM_KEY_STYLE, no_wrap=True)
        table.add_column("Name", style=common.NAME_STYLE, no_wrap=True)
        table.add_column("Owner", style=common.USER_STYLE, no_wrap=True)
        table.add_column("Size", style=common.SIZE_STYLE, no_wrap=True, justify="right")

        # Populate rows based on the last response.
        # We populate 'data' with the project material
        # so that we can sort of size using pandas.
        data: Dict[str, List[Any]] = {}
        total_size_bytes: int = 0
        row_number: int = 1
        if self.last_response and self.last_response.success:
            for project in self.last_response.msg["projects"]:
                total_size_bytes += project["size"]
                name: str = common.concat(project["name"], 14)
                data[f"{row_number}"] = [
                    project["project_id"],
                    name,
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
            for _, row in data_frame.sort_values(by=[3], ascending=False).iterrows():
                size_str: str = ""
                if row[3] > 0:
                    size_str = humanize.naturalsize(row[3], binary=True)
                table.add_row(
                    str(table.row_count + 1),
                    row[0],
                    row[1],
                    row[2],
                    size_str,
                )

        total_size_human: str = humanize.naturalsize(total_size_bytes, binary=True)
        title: str = f"Projects ({table.row_count}) [{total_size_human}]"
        return Panel(
            table if table.row_count else Text(),
            title=title,
            style=common.CORE_STYLE,
            padding=0,
        )
