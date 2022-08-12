"""A widget used to display DM Dataset information.
"""
from datetime import datetime
from typing import Any, Dict, List

import humanize
import pandas
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.style import Style
from squonk2.dm_api import DmApi

from squad import common
from squad.access_token import AccessToken
from .base import TopicRenderer

# Styles for instance phases.
_STAGE_STYLE: Dict[str, Style] = {
    "FORMATTING": Style(color="light_pink1"),
    "LOADING": Style(color="wheat1"),
    "DELETING": Style(color="green_yellow"),
    "DONE": Style(color="chartreuse4"),
    "FAILED": Style(color="bright_red"),
    "COPYING": Style(color="cyan1"),
}
_DEFAULT_STAGE_STYLE: Style = Style(color="green4")


class Datasets(TopicRenderer):
    """Displays datasets."""

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
                self.last_response = DmApi.get_available_datasets(self.access_token)
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
        table.add_column("Ver", style=common.NAME_STYLE, no_wrap=True, justify="right")
        table.add_column("Owner", style=common.USER_STYLE, no_wrap=True)
        table.add_column("Stage", style=common.USER_STYLE, no_wrap=True)
        table.add_column("Filename", style=common.NAME_STYLE, no_wrap=True)
        table.add_column("Size", style=common.SIZE_STYLE, no_wrap=True, justify="right")
        table.add_column("Published (UTC)", style=common.DATE_STYLE, no_wrap=True)
        table.add_column(
            "Used", style=common.USED_STYLE, no_wrap=True, justify="center"
        )

        # Populate rows based on the last response.
        # We populate 'data' with the project material
        # so that we can sort of size using pandas.
        data: Dict[str, List[Any]] = {}
        total_size_bytes: int = 0
        row_number: int = 1
        if self.last_response and self.last_response.success:
            for dataset in self.last_response.msg["datasets"]:
                dataset_id: str = dataset["dataset_id"]
                for dataset_version in dataset["versions"]:
                    size: int = dataset_version["size"]
                    total_size_bytes += size
                    data[f"{row_number}"] = [
                        dataset_id,
                        dataset_version["version"],
                        dataset_version["owner"],
                        dataset_version["processing_stage"],
                        dataset_version["file_name"],
                        size,
                        dataset_version["published"],
                        len(dataset_version["projects"]),
                    ]
                    row_number += 1

        # Populate rows based on the last response.
        if data:
            data_frame: pandas.DataFrame = pandas.DataFrame.from_dict(
                data, orient="index"
            )
            for _, row in data_frame.sort_values(by=[5], ascending=False).iterrows():
                stage: str = row[3]
                stage_text: Text = Text(
                    stage, style=_STAGE_STYLE.get(stage, _DEFAULT_STAGE_STYLE)
                )
                # Used is count of projects.
                # If zero use a cross.
                used = row[7]
                if used > 0:
                    used_text = Text(f"{used}", style=common.USED_STYLE)
                else:
                    used_text = common.CROSS
                table.add_row(
                    str(table.row_count + 1),
                    row[0],
                    str(row[1]),
                    row[2],
                    stage_text,
                    row[4],
                    humanize.naturalsize(row[5], binary=True),
                    row[6],
                    used_text,
                )

        total_size_human: str = humanize.naturalsize(total_size_bytes, binary=True)
        title: str = f"Datasets ({table.row_count}) [{total_size_human}]"
        return Panel(
            table if table.row_count else Text(),
            title=title,
            style=common.CORE_STYLE,
            padding=0,
        )
