"""A widget used to display DM Dataset information.
"""
from datetime import datetime
from typing import Any, Dict, List, Tuple

import humanize
import pandas
from rich.panel import Panel
from rich.text import Text
from rich.style import Style
from squonk2.dm_api import DmApi

from squad import common
from squad.access_token import AccessToken
from .base import SortOrder, TopicRenderer

# List of columns using names, styles and justification
_COLUMNS: List[Tuple[str, Style, str]] = [
    ("UID", common.UUID_STYLE, "left"),
    ("Ver", common.NAME_STYLE, "left"),
    ("Owner", common.USER_STYLE, "left"),
    ("Stage", None, "left"),
    ("Filename", common.NAME_STYLE, "left"),
    ("Size", common.STORAGE_SIZE_STYLE, "right"),
    ("Published (UTC)", common.DATE_STYLE, "left"),
    ("Used", None, "center"),
]

# Local styles for instance phases.
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

    def __init__(self) -> None:
        # Default sort column
        self.num_columns = len(_COLUMNS)
        self.sort_column = 6

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
        self.prepare_table(_COLUMNS)
        assert self.table

        # Populate rows based on the last response.
        # We populate 'data' with the project material
        # so that we can sort on 'launched' date using pandas.
        data: Dict[str, List[Any]] = {}
        row_number: int = 1
        if self.last_response and self.last_response.success:
            for dataset in self.last_response.msg["datasets"]:
                dataset_id: str = dataset["dataset_id"]
                for dataset_version in dataset["versions"]:
                    data[f"{row_number}"] = [
                        dataset_id,
                        dataset_version["version"],
                        dataset_version["owner"],
                        dataset_version["processing_stage"],
                        dataset_version["file_name"],
                        dataset_version["size"],
                        dataset_version["published"],
                        len(dataset_version["projects"]),
                    ]
                    row_number += 1

        # Populate rows based on the last response.
        total_size_bytes: int = 0
        if data:
            data_frame: pandas.DataFrame = pandas.DataFrame.from_dict(
                data, orient="index"
            )
            for _, row in data_frame.sort_values(
                by=[self.sort_column], ascending=self.sort_order == SortOrder.ASCENDING
            ).iterrows():
                stage: str = row[3]
                stage_text: Text = Text(
                    stage, style=_STAGE_STYLE.get(stage, _DEFAULT_STAGE_STYLE)
                )
                # Used is count of projects.
                # If zero use a cross.
                used = row[7]
                if used > 0:
                    used_text = Text(f"{used}", style=common.DATASET_USED_STYLE)
                else:
                    used_text = common.CROSS
                size: int = row[5]
                total_size_bytes += size
                self.table.add_row(
                    str(self.table.row_count + 1),
                    row[0],
                    str(row[1]),
                    row[2],
                    stage_text,
                    row[4],
                    humanize.naturalsize(size, binary=True),
                    row[6],
                    used_text,
                )

        total_size_human: str = humanize.naturalsize(total_size_bytes, binary=True)
        title: str = f"Datasets ({self.table.row_count}) [{total_size_human}]"
        return Panel(
            self.table,
            title=title,
        )
