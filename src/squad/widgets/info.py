"""A widget to display the summary information in the banner.
"""
from rich.panel import Panel
from rich.table import Table
from rich import box

from textual.widget import Widget

from squad import common


class InfoWidget(Widget):  # type: ignore
    """Displays general/summary information."""

    def render(self) -> Panel:
        """Render the latest information.

        This, for the moment is mini help screen (rather than using the footer).
        We display this in a table.
        """
        table = Table(
            show_header=False,
            collapse_padding=True,
            box=None,
        )
        table.add_column(
            "common-key", justify="right", style=common.HELP_KEY_STYLE, no_wrap=True
        )
        table.add_column("common-key-help", style=common.HELP_TEXT_STYLE, no_wrap=True)
        table.add_column("a-key", style=common.HELP_KEY_STYLE, no_wrap=True)
        table.add_column("a-key-help", style=common.HELP_TEXT_STYLE, no_wrap=True)
        table.add_column("b-key", style=common.HELP_KEY_STYLE, no_wrap=True)
        table.add_column("b-key-help", style=common.HELP_TEXT_STYLE, no_wrap=True)

        table.add_row("<Q>", "Quit", "<p>", "Projects", "<o>", "Orgs/Units")
        table.add_row("", "", "<d>", "Datasets", "<n>", "Personal units")
        table.add_row("", "", "<i>", "Instances", "<t>", "Products")
        table.add_row("", "", "<r>", "Defined exchange rates", "<a>", "Assets")
        table.add_row("", "", "<u>", "Undefined exchange rates", "<m>", "Merchants")
        table.add_row("", "", "<s>", "Service errors", "", "")

        return Panel(
            table,
            box=box.SIMPLE,
            style=common.CORE_STYLE,
            height=common.BANNER_HEIGHT,
            padding=0,
        )
