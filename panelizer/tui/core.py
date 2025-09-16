from textual import work
from textual.app import App, ComposeResult
from textual.widgets import Welcome
from textual_fspicker import SelectDirectory
from pathlib import Path


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

    def __init__(self):
        super().__init__()
        self.selected_input_dir: Path | None = None

    def compose(self) -> ComposeResult:
        yield Welcome()

    def on_button_pressed(self) -> None:
        self.show_file_picker()

    @work
    async def show_file_picker(self) -> None:
        self.selected_input_dir = await self.push_screen_wait(
            SelectDirectory(location=Path.home() / "Pictures")
        )
        if self.selected_input_dir:
            self.exit(self.selected_input_dir)
        else:
            self.exit(self.selected_input_dir)