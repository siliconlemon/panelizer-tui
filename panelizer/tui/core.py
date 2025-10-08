from pathlib import Path
from typing import Any
from textual import work
from textual.app import App
from textual.events import Resize
from textual.theme import Theme
from .screen_size import ScreenSize
from .screens.home import HomeScreen
from .screens.launch import LaunchScreen
from .screens.too_small import TooSmallScreen
from .state_machine import StateMachine

class PanelizerTUI(App[Any]):
    CSS_PATH = ["./css/globals.tcss"]
    TITLE = "Panelizer"
    SUB_TITLE = "Batch-fit your images onto single-color backgrounds"
    MIN_ROWS: int = 28
    MIN_COLS: int = 80
    SCREENS = {
        "launch": LaunchScreen,
        "home": HomeScreen,
        "too_small": TooSmallScreen,
    }
    DEFAULT_THEME = Theme(
        name="default",
        primary="#72b9cf",
        secondary="#757e82",
        accent="#ffffff",
        foreground="#dfe5ef",
        background="#1e1e1e",
        success="#a3be8c",
        warning="#ebcb8b",
        error="#ea4b4b",
        surface="#3b4252",
        panel="#292f3a",
        dark=True,
        variables={
            "block-cursor-text-style": "none",
            "footer-key-foreground": "#88c0d0",
        },
    )
    def __init__(self) -> None:
        super().__init__()
        self.set_themes()
        self.launch_started = False
        self.too_small_modal_open = False
        self.selected_input_dir: Path | None = None
        self.state_machine = StateMachine(ui=self)
        self.screen_size = ScreenSize(ui=self)

    async def on_resize(self, event: Resize) -> None:
        await self.screen_size.handle_on_resize(event.size.width, event.size.height)

    def set_themes(self) -> None:
        """Registers the default theme and sets it as the current theme."""
        for light_theme in ("textual-light", "catppuccin-latte", "solarized-lite"):
            self.unregister_theme(light_theme)
        self.register_theme(self.DEFAULT_THEME)
        self.theme = "default"

    @work
    async def run_state_machine(self) -> None:
        await self.state_machine.run()
