"""A widget used to display DM Instance information.
"""
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Tuple

import humanize
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
    ("Archived", None, "center"),
    ("Name", common.NAME_STYLE, "left"),
    ("Owner", common.USER_STYLE, "left"),
    ("Launched (UTC)", common.DATE_STYLE, "left"),
    ("Phase", common.USER_STYLE, "center"),
    ("Coins", common.COIN_STYLE, "right"),
    ("App/Job", None, "right"),
    ("Type", None, "left"),
]

# Styles for instance phases.
_PHASE_STYLE: Dict[str, Style] = {
    "RUNNING": Style(color="yellow1"),
    "COMPLETED": Style(color="green_yellow"),
    "FAILED": Style(color="red3"),
}
_DEFAULT_PHASE_STYLE: Style = Style(color="yellow3")

# Styles for instance phases.
_IMAGE_TYPE_STYLE: Dict[str, Style] = {
    "SIMPLE": Style(color="thistle1"),
    "NEXTFLOW": Style(color="orchid"),
}
_DEFAULT_IMAGE_TYPE_STYLE: Style = Style(color="bright_white")

# A lookup of instance application ID to 'friendly name.
# The key is the DM Application ID.
_APPS: Dict[str, str] = {"jupyternotebooks.squonk.it": "Jupyter Notebook"}

# A zero to compare against
_ZERO: Decimal = Decimal()


class Instances(TopicRenderer):
    """Displays instances."""

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
            for instance in self.last_response.msg["instances"]:
                archived: bool = False
                if "archived" in instance and instance["archived"]:
                    archived = True
                name: str = common.truncate(instance["name"], common.NAME_LENGTH)
                job: Text = Text(no_wrap=True)
                image_type: str = ""
                if instance["application_type"] == "JOB":
                    job.append(instance["job_job"], style=common.JOB_JOB_STYLE)
                    job.append("|")
                    job.append(instance["job_version"], style=common.JOB_VERSION_STYLE)
                    image_type = instance["job_image_type"]
                else:
                    # It's an application instance.
                    # Replace the application with something more friendly.
                    app_id = instance["application_id"]
                    if app_id in _APPS:
                        job.append(_APPS[app_id], style=common.APP_STYLE)
                    else:
                        job.append(app_id, style=common.APP_STYLE)
                if "coins" in instance:
                    coins: Decimal = Decimal(instance["coins"])
                else:
                    coins = Decimal()
                data[f"{row_number}"] = [
                    instance["id"],
                    archived,
                    name,
                    instance["owner"],
                    instance["launched"],
                    instance["phase"],
                    coins,
                    str(job),
                    image_type,
                ]
                row_number += 1

        if data:
            data_frame: pandas.DataFrame = pandas.DataFrame.from_dict(
                data, orient="index"
            )
            for _, row in data_frame.sort_values(
                by=[self.sort_column], ascending=self.sort_order == SortOrder.ASCENDING
            ).iterrows():
                phase: str = row[5]
                # Identify App/Job for prettier rendering.
                app_job: List[str] = row[7].split("|")
                if len(app_job) == 1:
                    # It's an application.
                    app_job_id: Text = Text(app_job[0], style=common.APP_STYLE)
                else:
                    # It's a job.
                    app_job_id = Text(app_job[0], style=common.JOB_JOB_STYLE)
                    app_job_id.append(" ")
                    app_job_id.append(app_job[1], style=common.JOB_VERSION_STYLE)
                # Sanitise coins
                coins = common.remove_exponent(Decimal(row[6]))
                if coins > _ZERO:
                    coins_str: str = humanize.intcomma(str(coins))
                    if "." not in coins_str:
                        coins_str += ".0"
                else:
                    coins_str = ""
                image_type = row[8]

                self.table.add_row(
                    str(self.table.row_count + 1),
                    row[0],
                    common.TICK if row[1] else common.CROSS,
                    row[2],
                    row[3],
                    row[4],
                    Text(phase, style=_PHASE_STYLE.get(phase, _DEFAULT_PHASE_STYLE)),
                    coins_str,
                    app_job_id,
                    Text(
                        image_type,
                        style=_IMAGE_TYPE_STYLE.get(
                            image_type, _DEFAULT_IMAGE_TYPE_STYLE
                        ),
                    ),
                )

        title: str = f"Instances ({self.table.row_count})"
        return Panel(
            self.table,
            title=title,
        )
