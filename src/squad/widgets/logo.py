"""A widget to display the application logo and version number.
"""
import os

from rich.panel import Panel
from rich.style import Style
from rich.text import Text
from rich import box
from textual.widget import Widget

from squad import common

# Styles specific to this widget.
_LOGO_A_STYLE: Style = Style(color="orange_red1", bold=True)
_LOGO_B_STYLE: Style = Style(color="bright_white")
_LOGO_V_STYLE: Style = Style(color="bright_white")

# Get the version of SquAd from the included VERSION file.
with open(
    os.path.join(os.path.dirname(__file__), "../VERSION"), encoding="utf8"
) as version_file:
    VERSION: str = version_file.read().strip()


class LogoWidget(Widget):  # type: ignore
    """The application logo, displays at the top of the terminal
    and displays the logo and the application version.
    When docked the 'size' is expected to be at least 14 so the logo
    is correctly aligned.
    """

    content = Text(no_wrap=True)
    content.append(" +-+-+-+-+-+\n", style=_LOGO_A_STYLE)
    content.append(" |", style=_LOGO_A_STYLE)
    content.append("S", style=_LOGO_B_STYLE)
    content.append("|", style=_LOGO_A_STYLE)
    content.append("q", style=_LOGO_B_STYLE)
    content.append("|", style=_LOGO_A_STYLE)
    content.append("u", style=_LOGO_B_STYLE)
    content.append("|", style=_LOGO_A_STYLE)
    content.append("A", style=_LOGO_B_STYLE)
    content.append("|", style=_LOGO_A_STYLE)
    content.append("d", style=_LOGO_B_STYLE)
    content.append("|\n", style=_LOGO_A_STYLE)
    content.append(" +-+-+-+-+-+\n", style=_LOGO_A_STYLE)
    version_str: str = f"{VERSION}"
    version_padding_size: int = len("+-+-+-+-+-+") - len(version_str)
    if version_padding_size < -1:
        version_padding_size = 0
    version_padding_size += 1
    version_padding: str = " " * version_padding_size
    content.append(f"{version_padding}{version_str}", style=_LOGO_V_STYLE)

    def render(self) -> Panel:
        """Render the widget."""
        return Panel(
            self.content,
            box=box.SIMPLE,
            style=common.CORE_STYLE,
            height=common.BANNER_HEIGHT,
            padding=0,
        )
