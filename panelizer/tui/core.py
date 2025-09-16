# panelizer/app.py

from pathlib import Path

from textual import work
from textual.app import App

from .screens.launch import LaunchScreen
from .widgets.picker import pick_directory


class PanelizerTUI(App[str]):
    CSS_PATH = None
    TITLE = "Panelizer"
    SUB_TITLE = "Batch-fit your images onto single-color backgrounds"
    COLORS = [
        "white",
        "maroon",
        "red",
        "purple",
        "fuchsia",
        "olive",
        "yellow",
        "navy",
        "teal",
        "aqua",
    ]

    SCREENS = {
        "launch": LaunchScreen,
    }

    def __init__(self):
        super().__init__()
        self.selected_input_dir: Path | None = None

    def on_mount(self) -> None:
        self.push_screen("launch")

    @work
    async def show_file_picker(self, location: Path) -> None:
        self.selected_input_dir = await self.push_screen_wait(
            pick_directory()
        )
        if self.selected_input_dir:
            self.exit(self.selected_input_dir)
        else:
            self.exit(self.selected_input_dir)