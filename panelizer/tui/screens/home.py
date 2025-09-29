import json
from pathlib import Path
from typing import Literal

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical, Container
from textual.events import Click
from textual.screen import Screen
from textual.widgets import Button, Static, Input
from textual_fspicker import SelectDirectory

from ..dialogs.file_select import FileSelectDialog


class HomeScreen(Screen[str]):
    CSS_PATH = ["../css/home.tcss"]
    BINDINGS = []

    def __init__(self, default_path: Path, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.selected_path: Path = default_path
        self.file_mode: Literal["all", "select"] = "all"
        self.selected_files: list[str] = []
        self.padding_top: int = 0
        self.padding_bottom: int = 0
        self.padding_left: int = 0
        self.padding_right: int = 0

    def compose(self) -> ComposeResult:
        with Vertical(id="home-vertical"):
            # Path row
            with Horizontal(id="path-row"):
                yield Static("📁", id="icon")
                yield Static(self.selected_path.as_posix(), id="path-field", classes="highlight hoverable")
            # File mode radio row
            with Horizontal(id="mode-row"):
                yield Button(
                    "All files", id="all-files-btn",
                    classes="file-mode selected" if self.file_mode == "all" else "file-mode"
                )
                yield Button(
                    self._select_label(),
                    id="select-files-btn",
                    classes="file-mode selected" if self.file_mode == "select" else "file-mode"
                )
            # Padding fields, two per row
            with Horizontal(id="pad-row-1"):
                yield Input(str(self.padding_left), placeholder="Left", id="pad-left", type="number")
                yield Static("%", id="pad-left-unit")
                yield Input(str(self.padding_right), placeholder="Right", id="pad-right", type="number")
                yield Static("%", id="pad-right-unit")
            with Horizontal(id="pad-row-2"):
                yield Input(str(self.padding_top), placeholder="Top", id="pad-top", type="number")
                yield Static("%", id="pad-top-unit")
                yield Input(str(self.padding_bottom), placeholder="Bottom", id="pad-bottom", type="number")
                yield Static("%", id="pad-bottom-unit")
            # Spacer to push start button to bottom
            yield Container(id="spacer")
            yield Button("Start Processing", id="start", variant="primary")

    def _select_label(self) -> str:
        """Returns the label for file selection button based on current selection."""
        if self.file_mode == "select" and self.selected_files:
            count = len(self.selected_files)
            if count == 1:
                return f"1 file: {Path(self.selected_files[0]).name}"
            if count <= 3:
                return f"{count} files: {', '.join(Path(f).name for f in self.selected_files)}"
            return f"{count} files selected"
        return "Select files"

    async def on_mount(self) -> None:
        """Updates the path display and padding fields on mount."""
        self._update_path_display()
        self._update_numbers()

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handles file mode buttons and start button."""
        if event.button.id == "all-files-btn":
            self.file_mode = "all"
            self.selected_files = []
            self._update_file_mode_buttons()

        elif event.button.id == "select-files-btn":
            self.file_mode = "select"
            files = await self.app.push_screen_wait(FileSelectDialog(self.selected_path))
            if files and len(files) > 0:
                self.selected_files = files  # Already strings
            else:
                self.selected_files = []
            self._update_file_mode_buttons()

        elif event.button.id == "start":
            self._emit_settings_and_close()

    async def on_click(self, event: Click) -> None:
        """Handles click on the path field to trigger directory picker."""
        if event.control.id == "path-field":
            new_dir = await self.app.push_screen_wait(
                SelectDirectory(location=self.selected_path)
            )
            if new_dir:
                self.selected_path = Path(new_dir)
                self._update_path_display()

    def _update_path_display(self) -> None:
        """Updates the path field display with the selected path."""
        self.query_one("#path-field", Static).update(self.selected_path.as_posix())

    def _update_file_mode_buttons(self) -> None:
        """Updates the button states and labels for file mode selection."""
        all_btn = self.query_one("#all-files-btn", Button)
        sel_btn = self.query_one("#select-files-btn", Button)
        all_btn.set_class(self.file_mode == "all", "selected")
        sel_btn.set_class(self.file_mode == "select", "selected")
        sel_btn.label = self._select_label()

    def _update_numbers(self) -> None:
        """Ensures the input fields show current padding values."""
        self.query_one("#pad-left", Input).value = str(self.padding_left)
        self.query_one("#pad-right", Input).value = str(self.padding_right)
        self.query_one("#pad-top", Input).value = str(self.padding_top)
        self.query_one("#pad-bottom", Input).value = str(self.padding_bottom)

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handles numeric input for padding fields and updates the state."""
        mapping = {
            "pad-left": "padding_left",
            "pad-right": "padding_right",
            "pad-top": "padding_top",
            "pad-bottom": "padding_bottom",
        }
        if event.input.id in mapping:
            try:
                val = int(event.value)
            except ValueError:
                val = 0
            setattr(self, mapping[event.input.id], max(0, min(100, val)))
            self._update_numbers()

    async def on_input_changed(self, event: Input.Changed) -> None:
        """Keeps internal state in sync while the user is editing padding fields."""
        await self.on_input_submitted(Input.Submitted(event.input, event.value))

    def _emit_settings_and_close(self) -> None:
        """Sends out JSON settings and closes the screen."""
        settings = {
            "path": str(self.selected_path),
            "files": self.selected_files if self.file_mode == "select" and self.selected_files
                else "ALL",
            "padding": {
                "left": self.padding_left,
                "right": self.padding_right,
                "top": self.padding_top,
                "bottom": self.padding_bottom,
            }
        }
        self.dismiss(json.dumps(settings))