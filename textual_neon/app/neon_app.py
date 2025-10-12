from importlib import resources
from typing import Any

from textual import work
from textual.app import App
from textual.events import Resize
from textual.theme import Theme

from .state_machine import StateMachine
from ..screens.too_small import ScreenSize, TooSmallScreen

NOT_REGISTERED_MSG = """
|
|   To use NeonApp, first register your screens and data exchanges in self.state_machine.
|
|   Example:
|   
|   YourApp(NeonApp):
|       def __init__(self) -> None:
|           super().__init__()
|           self.state_machine.register(
|               'home',
|               screen=HomeScreen,
|               next=None,
|               fallback='launch',
|               validate=lambda result: bool(result),
|               args_from_result=lambda result: (result,),
|          )
|
"""

class NeonApp(App[Any]):
    """
    A base class for textual_neon apps, ensuring basic setup, propper screen size with default values
    and the absense of light themes.
    """
    CSS_PATH = [resources.files("textual_neon.css").joinpath("globals.tcss")]
    MIN_ROWS: int = 40
    MIN_COLS: int = 80
    SCREENS = {}
    DEFAULT_THEME = Theme(
        name="default",
        primary="#36c8de",
        secondary="#98a1a5",
        accent="#ffffff",
        foreground="#c0c5cd",
        background="#1e1e1e",
        success="#63bd4a",
        warning="#ebb370",
        error="#ff524d",
        surface="#3b4252",
        panel="#27272d",
        dark=True,
        variables={
            "block-cursor-text-style": "none",
            "footer-key-foreground": "#88c0d0",
        },
    )

    def __init__(self) -> None:
        super().__init__()
        self.SCREENS.update({"too_small": TooSmallScreen})
        self.set_themes()
        self.app_started = False
        self.too_small_modal_open = False
        self.screen_size = ScreenSize(app=self)
        self.state_machine = StateMachine(app=self)

    async def on_resize(self, event: Resize) -> None:
        """Shows the TooSmallScreen if the terminal window gets too small."""
        await self.screen_size.handle_on_resize(event.size.width, event.size.height)

    def set_themes(self) -> None:
        """Registers the default theme and removes all pre-built light themes."""
        for light_theme in ("textual-light", "catppuccin-latte", "solarized-light"):
            self.unregister_theme(light_theme)
        self.register_theme(self.DEFAULT_THEME)
        self.theme = "default"

    @work
    async def run_state_machine(self) -> None:
        """
        Runs the app's state machine registered with data-driven states and transitions.
        """
        if not self.state_machine.registered:
            raise NotImplementedError(
                NOT_REGISTERED_MSG
            )
        await self.state_machine.run()
