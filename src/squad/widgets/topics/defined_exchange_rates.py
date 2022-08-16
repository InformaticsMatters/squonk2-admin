"""A textual widget used to display DM Exchange Rate information.
"""
from datetime import datetime
from typing import Dict, List, Tuple

import pandas
from rich.panel import Panel
from rich.style import Style
from squonk2.dm_api import DmApi

from squad import common
from squad.access_token import AccessToken
from .base import SortOrder, TopicRenderer

# List of columns using names, styles and justification
_COLUMNS: List[Tuple[str, Style, str]] = [
    ("Collection", common.JOB_COLLECTION_STYLE, "right"),
    ("Job", common.JOB_JOB_STYLE, "left"),
    ("Version", common.JOB_VERSION_STYLE, "left"),
    ("Rate", common.JOB_RATE_STYLE, "left"),
]


class DefinedExchangeRates(TopicRenderer):
    """Displays Job Exchange Rates."""

    def __init__(self) -> None:
        # Default sort column
        self.num_columns = len(_COLUMNS)
        self.sort_column = 0

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
                self.last_response = DmApi.get_job_exchange_rates(self.access_token)

        # Results in a table.
        self.prepare_table(_COLUMNS)
        assert self.table

        # Use pandas to sort results by collection and job.
        data: Dict[str, List[str]] = {}
        row_number: int = 1
        if self.last_response and self.last_response.success:
            for e_rate in self.last_response.msg["exchange_rates"]:
                data[f"{row_number}"] = [
                    e_rate["collection"],
                    e_rate["job"],
                    e_rate["version"],
                    e_rate["rate"],
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
                    row[3],
                )

        title: str = f"Defined exchange rates ({self.table.row_count})"
        return Panel(
            self.table,
            title=title,
        )
