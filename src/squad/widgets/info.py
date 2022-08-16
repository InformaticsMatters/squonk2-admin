"""A widget to display the help information in the banner.
"""
from rich.panel import Panel
from rich.style import Style
from rich.table import Table
from rich import box

from textual.widget import Widget

from squad import common

_HELP_KEY_STYLE: Style = Style(color="deep_sky_blue1", bold=True)
_HELP_TEXT_STYLE: Style = Style(color="grey50")


class InfoWidget(Widget):  # type: ignore
    """Displays general/help information."""

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
        table.add_column("a-key", justify="right", style=_HELP_KEY_STYLE, no_wrap=True)
        table.add_column("a-key-help", style=_HELP_TEXT_STYLE, no_wrap=True)
        table.add_column("b-key", style=_HELP_KEY_STYLE, no_wrap=True)
        table.add_column("b-key-help", style=_HELP_TEXT_STYLE, no_wrap=True)
        table.add_column("c-key", style=_HELP_KEY_STYLE, no_wrap=True)
        table.add_column("c-key-help", style=_HELP_TEXT_STYLE, no_wrap=True)
        table.add_column("d-key", style=_HELP_KEY_STYLE, no_wrap=True)
        table.add_column("d-key-help", style=_HELP_TEXT_STYLE, no_wrap=True)

        table.add_row(
            "<Q>",
            "Quit",
            "<p>",
            "Projects",
            "<o>",
            "Orgs/Units",
            "<left|right>",
            "Sort column",
        )
        table.add_row(
            "",
            "",
            "<d>",
            "Datasets",
            "<n>",
            "Personal units",
            "<up|down>",
            "Sort order",
        )
        table.add_row("", "", "<i>", "Instances", "<t>", "Products")
        table.add_row("", "", "<k>", "Tasks", "<a>", "Assets")
        table.add_row("", "", "<r>", "Defined exchange rates", "<m>", "Merchants")
        table.add_row("", "", "<u>", "Undefined exchange rates", "", "")
        table.add_row("", "", "<s>", "Service errors", "", "")

        return Panel(
            table,
            box=box.SIMPLE,
            style=common.CORE_STYLE,
            height=common.BANNER_HEIGHT,
            padding=0,
        )
