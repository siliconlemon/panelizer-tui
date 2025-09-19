from pathlib import Path

from textual import work
from textual.app import App
from textual.theme import Theme

from .screens.launch import LaunchScreen


class PanelizerTUI(App[Path]):
    CSS_PATH = "./css/globals.tcss"
    TITLE = "Panelizer"
    SUB_TITLE = "Batch-fit your images onto single-color backgrounds"
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
        self.selected_input_dir: Path | None = None

    def set_themes(self):
        for light_theme in ("textual-light", "catppuccin-latte", "solarized-lite"):
            self.unregister_theme(light_theme)
        self.register_theme(self.DEFAULT_THEME)
        self.theme = "default"

    @work
    async def on_mount(self) -> None:
        self.set_themes()
        path = await self.push_screen_wait("launch")
        self.exit(path)
