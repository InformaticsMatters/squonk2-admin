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

    environment: Environment = Environment()
    env: str = environment.environment()
    kc_hostname: str = environment.keycloak_hostname()
    user: str = environment.user()
    password: str = environment.user_password()

    as_access_token: Optional[str] = None
    dm_access_token: Optional[str] = None

    def on_mount(self) -> None:
        """Widget initialisation."""
        # Set an interval timer - we check the AS and DM APIs,
        # regularly trying to get the version of each.
        self.set_interval(20, self.refresh)

    def render(self) -> Panel:
        """Render the widget."""

        # Get access tokens (using anything we have)
        # Soon we will not need them - we just use it to indicate the
        # availability of the authentication service.
        self.as_access_token = AccessToken().get_as_access_token(
            prior_token=self.as_access_token
        )
        self.dm_access_token = AccessToken().get_dm_access_token(
            prior_token=self.dm_access_token
        )

        # If we got an access token we add a 'tick' (U2713) after the keyclock
        # hostname. If the token failed we add a 'cross' (U2717).
        access_token_status: str = "\u2713"
        access_token_status_style: Style = common.KEY_VALUE_SUCCESS_STYLE
        if self.as_access_token is None or self.dm_access_token is None:
            access_token_status = "\u2717"
            access_token_status_style = common.KEY_VALUE_ERROR_STYLE

        # Get the version of the DM API and the AS API
        dm_api_version: str = "Not connected"
        dm_api_version_style: Style = common.KEY_VALUE_ERROR_STYLE
        dm_ret_val: DmApiRv = DmApi.get_version(self.dm_access_token)
        if dm_ret_val.success:
            dm_api_version = f"v{dm_ret_val.msg['version']}"
            dm_api_version_style = common.KEY_VALUE_STYLE
        dm_api_version_value: Text = Text(dm_api_version, style=dm_api_version_style)

        as_api_version: str = "Not connected"
        as_api_version_style: Style = common.KEY_VALUE_ERROR_STYLE
        as_ret_val: AsApiRv = AsApi.get_version()
        if as_ret_val.success:
            as_api_version = f"v{as_ret_val.msg['version']}"
            as_api_version_style = common.KEY_VALUE_STYLE
        as_api_version_value: Text = Text(as_api_version, style=as_api_version_style)

        # DM Merchant (if we have a version)
        dm_merchant: Text = common.CROSS
        if self.dm_access_token and dm_ret_val.success:
            dm_ret_val = DmApi.get_account_server_registration(self.dm_access_token)
            if dm_ret_val.success:
                dm_merchant = Text(dm_ret_val.msg["name"])

        table = Table(
            show_header=False,
            collapse_padding=True,
            box=None,
        )
        table.add_column("Key", justify="right", style=common.KEY_STYLE, no_wrap=True)
        table.add_column("Value", style=common.KEY_VALUE_STYLE, no_wrap=True)

        # The 'Authentication host' is a special value,
        # it contains a 'tick' or 'cross' depending on whether a
        # token was obtained.
        kc_host = Text()
        kc_host.append(f"{self.kc_hostname}", style=common.KEY_VALUE_STYLE)
        kc_host.append(f" {access_token_status}", style=access_token_status_style)
        # The API lines are also dynamically styled.

        table.add_row("Env", self.env)
        table.add_row("Auth", kc_host)
        table.add_row("User", self.user)
        table.add_row("AS Ver", as_api_version_value)
        table.add_row("DM Ver", dm_api_version_value)
        table.add_row("Merchant", dm_merchant)

        return Panel(
            table,
            box=box.SIMPLE,
            style=common.CORE_STYLE,
            height=common.BANNER_HEIGHT,
            padding=0,
        )
