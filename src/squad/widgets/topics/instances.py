"""A widget used to display DM Instance information.
"""
from datetime import datetime
from typing import Any, Dict, List

import pandas
from rich.panel import Panel
from rich.table import Table
from rich.style import Style
from rich.text import Text

from squonk2.dm_api import DmApi, DmApiRv

from squad import common
from squad.access_token import AccessToken
from .base import TopicRenderer

# Styles for instance phases.
_PHASE_STYLE: Dict[str, Style] = {
    "RUNNING": Style(color="yellow1"),
    "COMPLETED": Style(color="green_yellow"),
    "FAILED": Style(color="red3"),
}
_DEFAULT_PHASE_STYLE: Style = Style(color="yellow3")

# A lookup of instance application ID to 'friendly name.
# The key is the DM Application ID.
_APPS: Dict[str, str] = {"jupyternotebooks.squonk.it": "Jupyter Notebook"}


class Instances(TopicRenderer):
    """Displays instances."""

    instances: List[Dict[str, Any]] = []

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
                    self.last_response = DmApi.get_available_instances(
                        self.access_token
                    )

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
        table.add_column("Launched (UTC)", style=common.DATE_STYLE, no_wrap=True)
        table.add_column("Phase", style=common.USER_STYLE, no_wrap=True)
        table.add_column("App/Job", style=common.JOB_STYLE, no_wrap=True)

        # Populate rows based on the last response.
        # We populate 'data' with the project material
        # so that we can sort on 'launched' date using pandas.
        data: Dict[str, List[Any]] = {}
        row_number: int = 1
        if self.last_response and self.last_response.success:
            for instance in self.last_response.msg["instances"]:
                name: str = common.concat(instance["name"], 14)
                job: Text = Text(no_wrap=True)
                if instance["application_type"] == "JOB":
                    job.append(instance["job_job"], style=common.JOB_STYLE)
                    job.append("|", style=common.SEPARATOR_STYLE)
                    job.append(instance["job_version"], style=common.VERSION_STYLE)
                else:
                    # It's an application instance.
                    # Replace the application with something more friendly.
                    app_id = instance["application_id"]
                    if app_id in _APPS:
                        job.append(_APPS[app_id], style=common.APP_STYLE)
                    else:
                        job.append(app_id, style=common.APP_STYLE)
                data[f"{row_number}"] = [
                    instance["id"],
                    name,
                    instance["owner"],
                    instance["launched"],
                    instance["phase"],
                    job,
                ]
                row_number += 1

        if data:
            # Create a data-frame and sort on 'launched' date (descending)
            # This will ensuer the most recently launched instance
            # is at the top of the list.
            data_frame: pandas.DataFrame = pandas.DataFrame.from_dict(
                data, orient="index"
            )
            for _, row in data_frame.sort_values(by=[3], ascending=False).iterrows():
                phase: str = row[4]
                table.add_row(
                    str(table.row_count + 1),
                    row[0],
                    row[1],
                    row[2],
                    row[3],
                    Text(phase, style=_PHASE_STYLE.get(phase, _DEFAULT_PHASE_STYLE)),
                    row[5],
                )

        title: str = f"Instances ({table.row_count})"
        return Panel(
            table if table.row_count else Text(),
            title=title,
            style=common.CORE_STYLE,
            padding=0,
        )
