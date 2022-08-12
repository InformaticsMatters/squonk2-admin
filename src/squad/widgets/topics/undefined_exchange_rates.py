"""A textual widget used to display DM Exchange Rate information.
"""
from datetime import datetime
from typing import Dict, List

import pandas
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from squonk2.dm_api import DmApi

from squad import common
from squad.access_token import AccessToken
from .base import TopicRenderer


class UndefinedExchangeRates(TopicRenderer):
    """Displays Job Exchange Rates that have no exchange rate."""

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
                self.last_response = DmApi.get_job_exchange_rates(
                    self.access_token, only_undefined=True
                )
            else:
                self.last_response = None

        # Results are presented in a table.
        table: Table = Table(
            collapse_padding=True,
            header_style=common.INDEX_STYLE,
            box=None,
        )
        table.add_column("", style=common.INDEX_STYLE, no_wrap=True, justify="right")
        table.add_column("Collection", style=common.COLLECTION_STYLE, no_wrap=True)
        table.add_column("Job", style=common.JOB_STYLE, no_wrap=True)
        table.add_column("Version", style=common.VERSION_STYLE, no_wrap=True)

        # Use pandas to sort results by collection and job.
        data: Dict[str, List[str]] = {}
        row_number: int = 1
        if self.last_response and self.last_response.success:
            for e_rate in self.last_response.msg["exchange_rates"]:
                data[f"{row_number}"] = [
                    e_rate["collection"],
                    e_rate["job"],
                    e_rate["version"],
                ]
                row_number += 1

        # Populate rows based on the last response.
        if data:
            data_frame: pandas.DataFrame = pandas.DataFrame.from_dict(
                data, orient="index"
            )
            cur_collection: str = ""
            for _, row in data_frame.sort_values(by=[0, 1]).iterrows():
                collection: str = ""
                if row[0] != cur_collection:
                    cur_collection = row[0]
                    collection = cur_collection
                table.add_row(
                    str(table.row_count + 1),
                    collection,
                    row[1],
                    row[2],
                )

        title: str = f"Undefined exchange rates ({table.row_count})"
        return Panel(
            table if table.row_count else Text(),
            title=title,
            style=common.CORE_STYLE,
            padding=0,
        )
