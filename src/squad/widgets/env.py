"""A textual widget used to display environment information.
"""
from typing import Optional

from rich.panel import Panel
from rich.style import Style
from rich.table import Table
from rich.text import Text
from rich import box
from textual.widget import Widget
from squonk2.dm_api import DmApi, DmApiRv
from squonk2.as_api import AsApi, AsApiRv

from squad import common
from squad.environment import Environment
from squad.access_token import AccessToken


class EnvironmentWidget(Widget):  # type: ignore
    """Displays the environment."""

    as_access_token: Optional[str] = None
    dm_access_token: Optional[str] = None

    def on_mount(self) -> None:
        """Widget initialisation."""
        # Set an interval timer - we check the AS and DM APIs
        # regularly trying to get the version of each.
        self.set_interval(20, self.refresh)

    def render(self) -> Panel:
        """Render the widget."""

        # Get access tokens (using anything we have)
        self.as_access_token = AccessToken.get_as_access_token(
            prior_token=self.as_access_token
        )
        self.dm_access_token = AccessToken.get_dm_access_token(
            prior_token=self.dm_access_token
        )

        # If we got a DM access token we add a 'tick' (U2713) after the keyclock
        # hostname. If the token failed we add a 'cross' (U2717).
        # We don't care about the AS, it's not used for the environment information.
        access_token_status: str = "\u2713"
        access_token_status_style: Style = common.KEY_VALUE_SUCCESS_STYLE
        if self.dm_access_token is None:
            access_token_status = "\u2717"
            access_token_status_style = common.KEY_VALUE_ERROR_STYLE

        # Get the version of the DM API and the AS API
        as_api_version: str = "Not connected"
        as_api_version_style: Style = common.KEY_VALUE_ERROR_STYLE
        as_ret_val: AsApiRv = AsApi.get_version()
        if as_ret_val.success:
            as_api_version = f"v{as_ret_val.msg['version']}"
            as_api_version_style = common.VERSION_STYLE
        as_api_version_value: Text = Text(as_api_version, style=as_api_version_style)

        dm_api_version: str = "Not connected"
        dm_api_version_style: Style = common.KEY_VALUE_ERROR_STYLE
        dm_ret_val: DmApiRv = DmApi.get_version(self.dm_access_token)
        if dm_ret_val.success:
            dm_api_version = f"v{dm_ret_val.msg['version']}"
            dm_api_version_style = common.VERSION_STYLE
        dm_api_version_value: Text = Text(dm_api_version, style=dm_api_version_style)

        # Information is presented in a table.
        table = Table(
            show_header=False,
            collapse_padding=True,
            box=None,
        )
        table.add_column("Key", justify="right", style=common.KEY_STYLE, no_wrap=True)
        table.add_column("Value", style=common.KEY_VALUE_STYLE, no_wrap=True)

        # The 'Authentication host' is a special value,
        # it contains a 'tick' or 'cross' depending on whether a
        # DM token was obtained.
        kc_host = Text()
        kc_host.append(
            f"{Environment.keycloak_hostname()}", style=common.KEY_VALUE_STYLE
        )
        kc_host.append(f" {access_token_status}", style=access_token_status_style)

        # The API lines are also dynamically styled.
        as_hostname: str = (
            Environment.as_hostname() if Environment.as_hostname() else "(Undefined)"
        )

        table.add_row("Env", Environment.environment())
        table.add_row("Auth", kc_host)
        table.add_row("AS", common.concat(as_hostname, 40))
        table.add_row("", as_api_version_value)
        table.add_row("DM", common.concat(Environment.dm_hostname(), 40))
        table.add_row("", dm_api_version_value)

        return Panel(
            table,
            box=box.SIMPLE,
            style=common.CORE_STYLE,
            height=common.BANNER_HEIGHT,
            padding=0,
        )
