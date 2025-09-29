from pathlib import Path
from textual import work
from textual.app import App
from textual.events import Resize
from textual.theme import Theme
from .screens.launch import LaunchScreen
from .screens.too_small import TooSmallScreen


class PanelizerTUI(App[Path]):
    CSS_PATH = ["./css/globals.tcss"]
    TITLE = "Panelizer"
    SUB_TITLE = "Batch-fit your images onto single-color backgrounds"
    MIN_ROWS: int = 28
    MIN_COLS: int = 50
    SCREENS = {
        "launch": LaunchScreen,
    }
    DEFAULT_THEME = Theme(
        name="default",
        primary="#88c0d0",
        secondary="#81a1c1",
        accent="#b48ead",
        foreground="#d8dee9",
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
        self._launch_started: bool = False
        self._too_small_modal_open: bool = False
        self.selected_input_dir: Path | None = None

    async def on_resize(self, event: Resize) -> None:
        """React to terminal resize events and show or close the 'too small' modal as needed."""
        await self.handle_too_small_on_resize(event.size.width, event.size.height)

    def set_themes(self) -> None:
        """Register the default theme and set it as the current theme."""
        for light_theme in ("textual-light", "catppuccin-latte", "solarized-lite"):
            self.unregister_theme(light_theme)
        self.register_theme(self.DEFAULT_THEME)
        self.theme = "default"

    async def show_too_small_modal(self) -> None:
        """Display the 'TooSmallScreen' modal if it isn't already open."""
        if not self._too_small_modal_open:
            self._too_small_modal_open = True
            await self.push_screen(
                TooSmallScreen(self.MIN_ROWS, self.MIN_COLS, width=self.size.width, height=self.size.height)
            )

    async def close_too_small_modal(self) -> None:
        """Close the 'TooSmallScreen' modal if it is open."""
        if self._too_small_modal_open:
            await self.pop_screen()
            self._too_small_modal_open = False

    async def handle_too_small_on_resize(self, width: int, height: int) -> None:
        """
        Show or hide the 'too small' modal based on current terminal dimensions.
        Launch the main screen if size permits it and the launch screen has not already started.
        """
        if height < self.MIN_ROWS or width < self.MIN_COLS:
            if not self._too_small_modal_open:
                await self.show_too_small_modal()
        else:
            if self._too_small_modal_open:
                await self.close_too_small_modal()
            if not self._launch_started:
                self._launch_started = True
                self.launch_launch_screen()

    @work
    async def launch_launch_screen(self) -> None:
        """Push and wait for the launch screen to finish, then exit the app."""
        path = await self.push_screen_wait("launch")
        self.exit(path)
