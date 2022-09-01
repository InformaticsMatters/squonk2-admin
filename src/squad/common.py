"""Common material (constants etc.).
"""
from decimal import Decimal

from rich.style import Style
from rich.text import Text
import textual

# The height and width of widgets in out 'banner' region.
BANNER_HEIGHT: int = 9
BANNER_ENVIRONMENT_WIDTH: int = 54
BANNER_LOGO_WIDTH: int = 14

# Length to truncate names to.
# "Informatics Matters" is 19 characters.
NAME_LENGTH: int = 20

# Styles
CORE_STYLE: Style = Style(color="grey54", bgcolor="black", bold=True)

# General styles, used in more than one topic renderer.
HOSTNAME_STYLE: Style = Style(color="cornflower_blue")

# Names of things
NAME_STYLE: Style = Style(color="gold3")
# Usernames, creators, owners etc.
USER_STYLE: Style = Style(color="bright_white")
# Datetime (UTC) strings
DATE_STYLE: Style = Style(color="honeydew2")
# Style for all out UUIDs
UUID_STYLE: Style = Style(color="deep_sky_blue1")
# Style for storage values
STORAGE_SIZE_STYLE: Style = Style(color="green3")
# Styles for Application IDs, Job collections, jobs and versions
APP_STYLE: Style = Style(color="cyan1")
JOB_COLLECTION_STYLE: Style = Style(color="plum1")
JOB_JOB_STYLE: Style = Style(color="magenta1")
JOB_VERSION_STYLE: Style = Style(color="wheat1")
JOB_SEPARATOR_STYLE: Style = Style(color="grey89")
JOB_RATE_STYLE: Style = Style(color="gold1", italic=True)
# Styles for Tasks
TASK_PURPOSE_VERSION_STYLE: Style = Style(color="dark_khaki")
# Style for product types, and coins
PRODUCT_TYPE_STYLE: Style = Style(color="light_slate_grey")
PRODUCT_FLAVOUR_STYLE: Style = Style(color="dark_orange")
COIN_STYLE: Style = Style(color="yellow1", italic=True)
COIN_OVER_ALLOWANCE_STYLE: Style = Style(color="yellow1", bgcolor="dark_orange")
COIN_OVER_LIMIT_STYLE: Style = Style(color="yellow1", bgcolor="deep_pink2")
COIN_DAY_STYLE: Style = Style(color="dark_olive_green3")
COIN_RESET_STYLE: Style = Style(color="orchid1")
# Style for messages
MSG_STYLE: Style = Style(color="cyan3")
# style for indices/line-numbers
INDEX_STYLE: Style = Style(color="grey50", italic=True)
# Merchants
MERCHANT_ID_STYLE: Style = Style(color="dark_sea_green2")
MERCHANT_NAME_STYLE: Style = Style(color="dark_sea_green2")
# Other stuff
DATASET_USED_STYLE: Style = Style(color="blue1")

# The following are used to format the table.
# Reverse is used in the header to indicate which column is being sorted.
REVERSE: Style = Style(reverse=True)

# Text icons.
TICK: Text = Text("\u2714", style=Style(color="green3", bold=True))
CROSS: Text = Text("\u02df", style=Style(color="red3", bold=True))


def log_info(msg: str) -> None:
    """Log an INFO message using the textual logger.

    WARNING: This can only be used after the textual app has been started."""
    textual.log(f"SquAd INFO # {msg}")


def log_warning(msg: str) -> None:
    """Log a WARNING message using the textual logger.

    WARNING: This can only be used after the textual app has been started."""
    textual.log(f"SquAd WARNING # {msg}")


def truncate(line: str, length: int) -> str:
    """Truncates a line of text to the specified length
    adding a single unicode character ellipsis if necessary.
    The returned string is no longer than the required length.
    """
    if len(line) <= length:
        return line
    return line[: length - 1] + "\u2026"


def remove_exponent(num: Decimal) -> Decimal:
    """Returns better decimals, i.e. 0.3000 becomes 0.3
    and 4.0 becomes 4.
    """
    return num.quantize(Decimal(1)) if num == num.to_integral() else num.normalize()
