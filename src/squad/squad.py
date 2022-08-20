#!/usr/bin/env python
"""The entry module for the Squad application."""
import argparse
import os
import sys
from typing import Optional

from textual.app import App
from squonk2.as_api import AsApi
from squonk2.dm_api import DmApi

from squad import common
from squad.environment import Environment
from squad.widgets.logo import LogoWidget
from squad.widgets.env import EnvWidget
from squad.widgets.info import InfoWidget
from squad.widgets.topic import TopicWidget

# Users set SQUONK2_LOGFILE to enable logging
# e.g. "export SQUONK2_LOGFILE=./squad.log"
_LOG: Optional[str] = os.environ.get("SQUONK2_LOGFILE")


class Squad(App):  # type: ignore
    """An example of a very simple Textual App"""

    async def on_load(self) -> None:
        """initialisation - prior to application starting - bind keys."""
        await self.bind("Q", "quit", "Quit")

        # Keys uses to switch the topic of the main display.
        await self.bind("a", "topic('assets')")
        await self.bind("d", "topic('datasets')")
        await self.bind("i", "topic('instances')")
        await self.bind("k", "topic('tasks')")
        await self.bind("m", "topic('merchants')")
        await self.bind("n", "topic('personal-units')")
        await self.bind("o", "topic('units')")
        await self.bind("p", "topic('projects')")
        await self.bind("r", "topic('defined-exchange-rates')")
        await self.bind("s", "topic('service-errors')")
        await self.bind("t", "topic('products')")
        await self.bind("u", "topic('undefined-exchange-rates')")

        # Sort column keys
        await self.bind("left", "sort_column('down')")
        await self.bind("right", "sort_column('up')")

        # Sort order keys
        await self.bind("up", "sort_order('ascending')")
        await self.bind("down", "sort_order('descending')")

    async def on_mount(self) -> None:
        """Widget initialisation - application start"""

        # Create a grid layout.
        # We'll have 4 columns (a-d) and 2 rows (banner, body).
        # Area 1 'a/top' will house the environment widget,
        # Area 2 'd/top' will house the logo widget and
        # the central Area 3 ('b/top' anc 'c/top') will house the help widget.
        # Area 4 will be the main body across all columns.
        grid = await self.view.dock_grid(edge="left")
        grid.add_column(
            name="a",
            min_size=common.BANNER_ENVIRONMENT_WIDTH,
            max_size=common.BANNER_ENVIRONMENT_WIDTH,
        )
        grid.add_column(
            name="b",
            fraction=10,
        )
        grid.add_column(
            name="c",
            fraction=10,
        )
        grid.add_column(
            name="d",
            min_size=common.BANNER_LOGO_WIDTH,
            max_size=common.BANNER_LOGO_WIDTH,
        )
        # The top row must display the environment and logo material.
        # It's narrow but must show all the lines.
        grid.add_row(
            name="banner", min_size=common.BANNER_HEIGHT, max_size=common.BANNER_HEIGHT
        )
        grid.add_row(name="body", fraction=100)

        # Now create widget areas spanning the rows and columns
        grid.add_areas(
            area1="a,banner",
            area2="b-start|c-end,banner",
            area3="d,banner",
            area4="a-start|d-end,body",
        )

        # Now put the widgets in the grid using the areas we've created.
        grid.place(
            area1=EnvWidget(),
            area2=InfoWidget(),
            area3=LogoWidget(),
            area4=TopicWidget(),
        )

    @staticmethod
    async def action_topic(topic: str) -> None:
        """Reacts to key-press, given a topic as an argument,
        and passes the argument to the TopicWidget in order to change the
        content of the main 'topic' area.
        """
        TopicWidget.set_topic(topic)

    @staticmethod
    async def action_sort_column(up_down: str) -> None:
        """Reacts to a left/right cursor key-press, given 'up' or 'down'."""
        TopicWidget.sort_column(up_down)

    @staticmethod
    async def action_sort_order(up_down: str) -> None:
        """Reacts to a left/right cursor key-press, given 'ascending' or 'descending'."""
        TopicWidget.sort_order(up_down)


def main() -> int:
    """Application entry point, called when the module is executed."""

    parser = argparse.ArgumentParser(prog="squad", description="Squonk2 Admin (SquAd)")
    parser.add_argument(
        "name",
        nargs="?",
        help="The environment name to use. This is the name"
        " of the environment, e.g. dls-dev, not the"
        " location of the environments file. If not provided"
        " SquAd will use the environment value defined"
        " in the environments file.",
    )
    parser.add_argument(
        "--enable-stderr",
        help="Used for debug. Normally stderr is hidden from"
        " the console to avoid disturbing the textual"
        " framework. But when there are problems we"
        " need to see the stderr stream. Set this"
        " to allow stderr to appear ion the console.",
        action="store_true",
    )
    args = parser.parse_args()

    # Load the DM/AS config from the environment file
    # we do this here to make sure the environment is intact
    # before allowing any widgets to use it.
    name: Optional[str] = args.name if args.name else None
    try:
        Environment.init(name=name)
    except Exception as ex:  # pylint: disable=broad-except
        print(f"Error loading environment: {ex}")
        sys.exit(1)

    # Set the API URLs for the AS and DM
    # based on the environment we've just read.
    if Environment.as_api():
        AsApi.set_api_url(Environment.as_api(), verify_ssl_cert=False)
    DmApi.set_api_url(Environment.dm_api(), verify_ssl_cert=False)

    # Redirect stderr to avoid any potential SSL errors
    # e.g. the 'ssl.SSLCertVerificationError'
    # which will get written to the output stream
    # from interfering with the TUI.
    #
    # We can't write to stdout/stderr and use Textual.
    if not args.enable_stderr:
        sys.stderr = open(os.devnull, "w", encoding="utf-8")

    # Run our app class
    Squad.run(title="SquAd", log=_LOG)

    # If we get here, return 0 to indicate success
    # after restoring stderr.
    if not args.enable_stderr:
        sys.stderr.close()
    return 0


# -----------------------------------------------------------------------------
# MAIN
# -----------------------------------------------------------------------------
if __name__ == "__main__":

    _RET_VAL: int = main()
    if _RET_VAL != 0:
        sys.exit(_RET_VAL)
