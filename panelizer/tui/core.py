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
    MIN_ROWS = 35
    MIN_COLS = 60
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

    def __init__(self):
        super().__init__()
        self._launch_started: bool = False
        self._too_small_modal_open: bool = False
        self.selected_input_dir: Path | None = None

    @work
    async def on_mount(self) -> None:
        self.set_themes()
        if self.size.width >= self.MIN_COLS and self.size.height >= self.MIN_ROWS:
            self._launch_started = True
            path = await self.push_screen_wait("launch")
            self.exit(path)
        else:
            await self.show_too_small_modal()

    async def on_resize(self, event: Resize) -> None:
        await self.handle_too_small_on_resize(event.size.width, event.size.height)

    def set_themes(self):
        for light_theme in ("textual-light", "catppuccin-latte", "solarized-lite"):
            self.unregister_theme(light_theme)
        self.register_theme(self.DEFAULT_THEME)
        self.theme = "default"

    async def show_too_small_modal(self):
        if not self._too_small_modal_open:
            self._too_small_modal_open = True
            await self.push_screen(
                TooSmallScreen(self.MIN_ROWS, self.MIN_COLS, width=self.size.width, height=self.size.height)
            )

    async def close_too_small_modal(self):
        if self._too_small_modal_open:
            await self.pop_screen()
            self._too_small_modal_open = False

    async def handle_too_small_on_resize(self, width: int, height: int):
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
    async def launch_launch_screen(self):
        path = await self.push_screen_wait("launch")
        self.exit(path)
