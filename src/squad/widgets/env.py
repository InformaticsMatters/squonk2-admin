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

_KEY_STYLE: Style = Style(color="orange_red1")
_KEY_VALUE_STYLE: Style = Style(color="bright_white")
_VALUE_ERROR_STYLE: Style = Style(
    color="bright_yellow", bgcolor="bright_red", bold=True
)


class EnvWidget(Widget):  # type: ignore
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

        # Get the version of the DM API and the AS API
        as_api_version: str = "- NO RESPONSE -"
        as_api_version_style: Style = _VALUE_ERROR_STYLE
        as_ret_val: AsApiRv = AsApi.get_version()
        if as_ret_val.success:
            as_api_version = f"{as_ret_val.msg['version']}"
            as_api_version_style = _KEY_VALUE_STYLE
        as_api_version_value: Text = Text(as_api_version, style=as_api_version_style)

        dm_api_version: str = "- NO RESPONSE -"
        dm_api_version_style: Style = _VALUE_ERROR_STYLE
        dm_ret_val: DmApiRv = DmApi.get_version(self.dm_access_token)
        if dm_ret_val.success:
            dm_api_version = f"{dm_ret_val.msg['version']}"
            dm_api_version_style = _KEY_VALUE_STYLE
        dm_api_version_value: Text = Text(dm_api_version, style=dm_api_version_style)

        # Information is presented in a table.
        table = Table(
            show_header=False,
            collapse_padding=True,
            box=None,
        )
        table.add_column("Key", style=_KEY_STYLE, no_wrap=True, justify="right")
        table.add_column("Value", style=_KEY_VALUE_STYLE, no_wrap=True)

        # The 'Authentication host' is a special value,
        # it contains a 'tick' or 'cross' depending on whether a
        # DM token was obtained.
        kc_host = Text(f"{Environment.keycloak_hostname()} ", style=_KEY_VALUE_STYLE)
        if self.dm_access_token:
            kc_host.append(common.TICK)
        else:
            kc_host.append(common.CROSS)

        # The API lines are also dynamically styled.
        as_hostname: Optional[str] = Environment.as_hostname()
        if as_hostname:
            as_hostname_style: Style = _KEY_VALUE_STYLE
        else:
            as_hostname = "(Undefined)"
            as_hostname_style = _VALUE_ERROR_STYLE

        table.add_row("Env", Environment.environment())
        table.add_row("Auth", kc_host)
        table.add_row(
            "AS", Text(common.truncate(as_hostname, 40), style=as_hostname_style)
        )
        table.add_row("v", as_api_version_value)
        table.add_row("DM", common.truncate(Environment.dm_hostname(), 40))
        table.add_row("v", dm_api_version_value)

        return Panel(
            table,
            box=box.SIMPLE,
            style=common.CORE_STYLE,
            height=common.BANNER_HEIGHT,
            padding=0,
        )
