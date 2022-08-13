"""A widget to display the application logo and version number.
"""
import os

from rich.panel import Panel
from rich.text import Text
from rich import box
from textual.widget import Widget

from squad import common

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
    content.append(" +-+-+-+-+-+\n", style=common.LOGO_STYLE)
    content.append(" |", style=common.LOGO_STYLE)
    content.append("S", style=common.KEY_VALUE_STYLE)
    content.append("|", style=common.LOGO_STYLE)
    content.append("q", style=common.KEY_VALUE_STYLE)
    content.append("|", style=common.LOGO_STYLE)
    content.append("u", style=common.KEY_VALUE_STYLE)
    content.append("|", style=common.LOGO_STYLE)
    content.append("A", style=common.KEY_VALUE_STYLE)
    content.append("|", style=common.LOGO_STYLE)
    content.append("d", style=common.KEY_VALUE_STYLE)
    content.append("|\n", style=common.LOGO_STYLE)
    content.append(" +-+-+-+-+-+\n", style=common.LOGO_STYLE)
    version_str: str = f"{VERSION}"
    version_padding_size: int = len("+-+-+-+-+-+") - len(version_str)
    if version_padding_size < -1:
        version_padding_size = 0
    version_padding_size += 1
    version_padding: str = " " * version_padding_size
    content.append(f"{version_padding}{version_str}")

    def render(self) -> Panel:
        """Render the widget."""
        return Panel(
            self.content,
            box=box.SIMPLE,
            style=common.CORE_STYLE,
            height=common.BANNER_HEIGHT,
            padding=0,
        )
