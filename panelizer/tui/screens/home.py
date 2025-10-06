import json
from pathlib import Path
from typing import Literal

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical, Container, Grid
from textual.screen import Screen
from textual.widgets import Button, Input, Header, Static
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
        yield Header()
        with Vertical(id="home-vertical"):
            with Horizontal(id="path-row"):
                yield Button(self.selected_path.as_posix(), id="path-btn", classes="extra-wide-btn")
            with Horizontal(id="main-row"):
                with Vertical(id="input-column"):
                    with Grid(id="pad-grid"):
                        for element_id, value, label in [
                            ("pad-left", self.padding_left, "Left"),
                            ("pad-right", self.padding_right, "Right"),
                            ("pad-top", self.padding_top, "Top"),
                            ("pad-bottom", self.padding_bottom, "Bottom"),
                        ]:
                            with Vertical(classes="pad-grid-cell"):
                                yield Static(label, classes="pad-label")
                                with Horizontal(classes="pad-entry-row"):
                                    yield Input(str(value), id=element_id, classes="pad-entry", type="number")
                                    yield Static("%", classes="pad-suffix", disabled=True)
                yield Vertical(id="future-feature")
            with Horizontal(id="file-select-grid"):
                yield Button(
                    label=self._set_all_files_btn_label(), id="all-files-btn",
                    classes="toggle-btn gap-right toggled"
                        if self.file_mode == "all"
                        else "toggle-btn gap-right"
                )
                yield Button(
                    label=self._set_select_files_btn_label(), id="select-files-btn",
                    classes="toggle-btn toggled gap-left"
                        if self.file_mode == "select"
                        else "toggle-btn gap-left"
                )
            yield Button("Start Processing", id="start-btn", classes="extra-wide-btn", variant="primary")

    @staticmethod
    def _highlight_toggled_text(text: str) -> str:
        return f"\\[ {text} ]"

    def _set_all_files_btn_label(self) -> str:
        """Returns the label for the 'all-files-btn' button based on if it's toggled."""
        if self.file_mode == "all":
            return self._highlight_toggled_text("All Files")
        return "All Files"

    def _set_select_files_btn_label(self) -> str:
        """Returns the label for 'select files' button based on if it and any files are selected."""
        if self.file_mode == "select" and self.selected_files:
            count = len(self.selected_files)
            if count == 1:
                label_text = f"1 file: {Path(self.selected_files[0]).name}"
            elif count <= 3:
                file_names = ', '.join(Path(f).name for f in self.selected_files)
                label_text = f"{count} Files: {file_names}"
            else:
                label_text = f"{count} Files Selected"
            return self._highlight_toggled_text(label_text)
        return "Select Files"

    async def on_mount(self) -> None:
        self._update_path_display()
        self._update_file_mode_buttons()
        self._update_numbers()

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "all-files-btn":
            self.file_mode = "all"
            self.selected_files = []
            self._update_file_mode_buttons()
            event.stop()
        elif event.button.id == "select-files-btn":
            self.file_mode = "select"
            files = await self.app.push_screen_wait(FileSelectDialog(self.selected_path))
            self.selected_files = files or []
            self._update_file_mode_buttons()
            event.stop()
        elif event.button.id == "start-btn":
            self._emit_settings_and_close()
            event.stop()
        elif event.button.id == "path-btn":
            new_dir = await self.app.push_screen_wait(
                SelectDirectory(location=self.selected_path)
            )
            if new_dir:
                self.selected_path = Path(new_dir)
                self._update_path_display()
            event.stop()

    def _update_path_display(self) -> None:
        path_btn = self.query_one("#path-btn", Button)
        path = self.selected_path.as_posix()
        path_btn.label = path

    def _update_file_mode_buttons(self) -> None:
        all_btn = self.query_one("#all-files-btn", Button)
        sel_btn = self.query_one("#select-files-btn", Button)
        all_btn.set_class(self.file_mode == "all", "toggled")
        sel_btn.set_class(self.file_mode == "select", "toggled")
        sel_btn.label = self._set_select_files_btn_label()

    def _update_numbers(self) -> None:
        self.query_one("#pad-left", Input).value = str(self.padding_left)
        self.query_one("#pad-right", Input).value = str(self.padding_right)
        self.query_one("#pad-top", Input).value = str(self.padding_top)
        self.query_one("#pad-bottom", Input).value = str(self.padding_bottom)

    async def on_input_changed(self, event: Input.Changed) -> None:
        await self.on_input_submitted(Input.Submitted(event.input, event.value))

    async def on_input_submitted(self, event: Input.Submitted) -> None:
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
            val = max(0, min(100, val))
            setattr(self, mapping[event.input.id], val)
            self._update_numbers()

    def _emit_settings_and_close(self) -> None:
        settings = {
            "path": str(self.selected_path),
            "files": self.selected_files if self.file_mode == "select" and self.selected_files else "ALL",
            "padding": {
                "left": self.padding_left,
                "right": self.padding_right,
                "top": self.padding_top,
                "bottom": self.padding_bottom,
            }
        }
        self.dismiss(json.dumps(settings))
