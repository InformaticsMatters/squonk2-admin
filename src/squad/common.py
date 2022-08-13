"""Common material (constants etc.).
"""
from rich.style import Style
from rich.text import Text
import textual

# The height and width of widgets in out 'banner' region.
BANNER_HEIGHT: int = 8
BANNER_ENVIRONMENT_WIDTH: int = 54
BANNER_LOGO_WIDTH: int = 14

# Styles
CORE_STYLE: Style = Style(color="grey70", bgcolor="black")
LOGO_STYLE: Style = Style(color="orange_red1", bold=True)
HELP_KEY_STYLE: Style = Style(color="deep_sky_blue1", bold=True)
HELP_TEXT_STYLE: Style = Style(color="grey50")
INDEX_STYLE: Style = Style(color="grey50", italic=True)
KEY_STYLE: Style = Style(color="orange_red1", bold=True)
KEY_VALUE_STYLE: Style = Style(color="bright_white")
KEY_VALUE_ERROR_STYLE: Style = Style(color="bright_red", italic=True)
KEY_VALUE_SUCCESS_STYLE: Style = Style(color="green3")
ITEM_KEY_STYLE: Style = Style(color="deep_sky_blue1")
USER_STYLE: Style = Style(color="bright_white")
NAME_STYLE: Style = Style(color="gold3")
SIZE_STYLE: Style = Style(color="green3")
TYPE_STYLE: Style = Style(color="light_slate_grey")
USED_STYLE: Style = Style(color="blue1")

COIN_STYLE: Style = Style(color="yellow1")
COIN_OVERSPEND_STYLE: Style = Style(color="yellow1", bgcolor="dark_goldenrod")
COIN_LIMIT_STYLE: Style = Style(color="yellow1", bgcolor="deep_pink2")
DATE_STYLE: Style = Style(
    color="plum1",
)

APP_STYLE: Style = Style(color="cyan1")

COLLECTION_STYLE: Style = Style(color="deep_sky_blue1")
JOB_STYLE: Style = Style(color="gold3")
VERSION_STYLE: Style = Style(color="orchid1")
RATE_STYLE: Style = Style(color="green3")
SEPARATOR_STYLE: Style = Style(color="bright_white")

MERCHANT_ID_STYLE: Style = Style(color="dark_sea_green2")
MERCHANT_STYLE: Style = Style(color="dark_sea_green2")

REVERSE: Style = Style(reverse=True)

# Predefined/common text items
TICK: Text = Text("\u2713", style=Style(color="green3", bold=True, italic=True))
CROSS: Text = Text("\u2717", style=Style(color="red3", bold=True, italic=True))


def log_info(msg: str) -> None:
    """Log an INFO message using the textual logger.
    CAUTION: This can only be used after the textual app has been started."""
    textual.log(f"SquAd INFO # {msg}")


def log_warning(msg: str) -> None:
    """Log a WARNING message using the textual logger.
    CAUTION: This can only be used after the textual app has been started."""
    textual.log(f"SquAd WARNING # {msg}")


def concat(line: str, length: int) -> str:
    """Concatenate a line of text to the specified length
    adding unicode ellipsis if necessary.
    """
    if len(line) <= length:
        return line
    return line[: length - 1] + "\u2026"
