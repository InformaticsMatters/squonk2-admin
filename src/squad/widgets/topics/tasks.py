"""A widget used to display DM Task information.
"""
from datetime import datetime
from typing import Any, Dict, List, Tuple

import pandas
from rich.panel import Panel
from rich.style import Style
from rich.text import Text

from squonk2.dm_api import DmApi, DmApiRv

from squad import common
from squad.access_token import AccessToken
from .base import SortOrder, TopicRenderer

# List of columns using names, styles and justification
_COLUMNS: List[Tuple[str, Style, str]] = [
    ("UUID", common.UUID_STYLE, "left"),
    ("Created (UTC)", common.DATE_STYLE, "left"),
    ("Purpose", None, "left"),
    ("Purpose UUID", common.UUID_STYLE, "left"),
    ("Version", common.TASK_PURPOSE_VERSION_STYLE, "left"),
    ("Done", None, "center"),
    ("Code", None, "center"),
    ("Removal", None, "center"),
]

# Styles for instance phases.
_PURPOSE_STYLE: Dict[str, Style] = {
    "DATASET": Style(color="magenta"),
    "FILE": Style(color="bright_cyan"),
    "INSTANCE": Style(color="green"),
    "PROJECT": Style(color="bright_white"),
}
_DEFAULT_PURPOSE_STYLE: Style = Style(color="yellow3")

# Value used for unset exit_code
_UNSET_EXIT_CODE: int = -999_999_999


class Tasks(TopicRenderer):
    """Displays tasks."""

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
            self.access_token = AccessToken.get_dm_access_token(
                prior_token=self.access_token
            )
            self.last_response_time = now
            if self.access_token:

                # Got a token, time to get a new set of results...
                set_admin_response: DmApiRv = DmApi.set_admin_state(
                    self.access_token, admin=True
                )
                if set_admin_response.success:
                    self.last_response = DmApi.get_available_tasks(self.access_token)
            else:
                self.last_response = None

        # Results in a table.
        self.prepare_table(_COLUMNS)
        assert self.table

        # Populate rows based on the last response.
        # We populate 'data' with the project material
        # so that we can sort on 'created' date using pandas.
        data: Dict[str, List[Any]] = {}
        row_number: int = 1
        if self.last_response and self.last_response.success:
            for task in self.last_response.msg["tasks"]:
                data[f"{row_number}"] = [
                    task["id"],
                    task["created"],
                    task["purpose"],
                    task["purpose_id"],
                    task.get("purpose_version", 0),
                    task.get("done", False),
                    task.get("exit_code", _UNSET_EXIT_CODE),
                    task.get("removal", False),
                ]
                row_number += 1

        if data:
            data_frame: pandas.DataFrame = pandas.DataFrame.from_dict(
                data, orient="index"
            )
            for _, row in data_frame.sort_values(
                by=[self.sort_column], ascending=self.sort_order == SortOrder.ASCENDING
            ).iterrows():
                purpose: str = row[2]
                # Render exit code.
                # Green or red.
                # But cater for unset codes.
                exit_code: int = row[6]
                exit_code_str = str(exit_code)
                exit_code_style: Style = Style(color="green1")
                if exit_code == _UNSET_EXIT_CODE:
                    exit_code_str = "-"
                    exit_code_style = Style(color="bright_black")
                elif exit_code != 0:
                    exit_code_style = Style(color="bright_red", reverse=True)
                # Populate the row...
                self.table.add_row(
                    str(self.table.row_count + 1),
                    row[0],
                    row[1],
                    Text(
                        purpose,
                        style=_PURPOSE_STYLE.get(purpose, _DEFAULT_PURPOSE_STYLE),
                    ),
                    row[3],
                    str(row[4]) if row[4] else "",
                    common.TICK if row[5] else common.CROSS,
                    Text(exit_code_str, style=exit_code_style),
                    common.TICK if row[7] else common.CROSS,
                )

        title: str = f"Tasks ({self.table.row_count})"
        return Panel(
            self.table,
            title=title,
        )
