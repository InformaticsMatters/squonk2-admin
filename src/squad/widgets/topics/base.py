"""The base class for all widgets."""
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from enum import Enum
from typing import List, Optional, Tuple, Union

from rich import box
from rich.panel import Panel
from rich.style import Style
from rich.table import Table
from squonk2.as_api import AsApiRv
from squonk2.dm_api import DmApiRv

from squad import common


class SortOrder(Enum):
    """The sort order for a table."""

    ASCENDING = 1
    DESCENDING = 2


class TopicRenderer(ABC):
    """The base class for all widgets."""

    access_token: Optional[str] = None

    # A Table,
    # initialised in prepare_table()
    # and populated by the render() method.
    table: Optional[Table] = None

    # Period between calls to the DmApi.
    # We do not call the DmApi more frequently than this.
    refresh_interval: timedelta = timedelta(seconds=20)
    # The last response from the DmApi (or AsApi) in a renderer.
    last_response: Optional[Union[DmApiRv, AsApiRv]] = None
    # The time we got the last response
    last_response_time: Optional[datetime] = None

    # What column do we sort topic results (1..N) and what's the order?
    # These are adjusted by the specific topic renderer.
    sort_column: int = 0
    sort_order: SortOrder = SortOrder.DESCENDING
    # how many columns does the topic have?
    num_columns: int = 1

    def prepare_table(self, columns: List[Tuple[str, Style, str]]) -> None:
        """Prepare the table for rendering. This is called from each
        renderer when rendering is required.
        """
        # Results in a table.
        self.table = Table(
            collapse_padding=True,
            box=box.ASCII,
            expand=True,
            padding=(0, 0),
            pad_edge=False,
        )
        self.table.add_column(
            "", style=common.INDEX_STYLE, no_wrap=True, justify="right"
        )
        c_index: int = 0
        for item in columns:
            header_style: Style = common.INDEX_STYLE
            name: str = item[0]
            if c_index == self.sort_column:
                # There is a response. We are setting the selected sort column,
                # so 'invert' the header and add a sort order icon (arrow)
                if self.sort_order == SortOrder.ASCENDING:
                    # Up Triangle
                    name += " \u25b2"
                else:
                    # Down Triangle
                    name += " \u25bc"
                header_style = Style.combine([header_style, common.REVERSE])
            c_index += 1
            # Justification is centered by default.
            justify: str = item[2] if item[2] else "center"
            self.table.add_column(
                name,
                style=item[1],
                no_wrap=True,
                justify=justify,
                header_style=header_style,
            )

    def adjust_sort_column(self, up_down: str) -> None:
        """Widget increments its copy of the sort column."""
        if up_down == "down" and self.sort_column > 0:
            self.sort_column -= 1
        elif up_down == "up" and self.sort_column < self.num_columns - 1:
            self.sort_column += 1

    def adjust_sort_order(self, up_down: str) -> None:
        """Sets sort order based on string value, whcih will be one
        of 'ascending' or 'descending'.
        """
        if up_down == "descending":
            self.sort_order = SortOrder.DESCENDING
        elif up_down == "ascending":
            self.sort_order = SortOrder.ASCENDING

    @abstractmethod
    def render(self) -> Panel:
        """Render the widget."""
