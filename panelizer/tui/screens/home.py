import json
from pathlib import Path
from typing import Literal

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Input, Header, Select
from textual_fspicker import SelectDirectory

from textual_neon import FileSelectDialog
from textual_neon import DefaultsPalette, CompleteInputGrid, CompleteSelect, Toggle, NeonButton


class HomeScreen(Screen[str]):
    CSS_PATH = ["../css/home.tcss"]
    BINDINGS = []

    def __init__(self, default_path: Path, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.selected_path: Path = default_path
        self.file_mode: Literal["all", "select"] = "all"
        self.selected_files: list[str] = []
        self.img_padding_left: int = 0
        self.img_padding_right: int = 0
        self.img_padding_top: int = 0
        self.img_padding_bottom: int = 0
        self.background_color: str = "white"
        self.background_color_options: list[tuple[str, str]] = [
            ("White", "white"),
            ("Light Gray", "lightgray"),
            ("Dark Gray", "darkgray"),
            ("Black", "black"),
        ]
        self.split_image_active: bool = False

    def compose(self) -> ComposeResult:
        yield Header(icon="●")
        with Vertical(id="home-row"):
            with Horizontal(id="path-row"):
                yield NeonButton(self.selected_path.as_posix(), id="path-btn", classes="extra-wide-btn")
            with Horizontal(id="main-row"):

                with Vertical(id="first-column"):
                    yield CompleteInputGrid(
                        rows=2,
                        columns=2,
                        values=[self.img_padding_left, self.img_padding_right, self.img_padding_top, self.img_padding_bottom],
                        labels=["Left", "Right", "Top", "Bottom"],
                        input_ids=["pad-left", "pad-right", "pad-top", "pad-bottom"],
                        units=["%", "%", "%", "%"],
                        id="pad-grid"
                    )
                    yield Toggle(
                        switch_id="split-wide-toggle-switch",
                        text="Split Wide Images",
                        is_active=self.split_image_active,
                        id="split-wide-toggle",
                    )

                with Vertical(id="second-column"):
                    yield CompleteSelect(
                        select_id="bg-select",
                        label="Background Color",
                        initial=self.background_color,
                        options=self.background_color_options,
                    )
                    yield DefaultsPalette(
                        save_btn_id="save-defaults-btn",
                        restore_btn_id="restore-defaults-btn",
                        reset_btn_id="reset-defaults-btn",
                        widget_id="defaults-widget",
                        label="Default Values",
                    )

            with Horizontal(id="file-select-grid"):
                yield NeonButton(
                    label=self._set_all_files_btn_label(), id="all-files-btn",
                    classes="toggle-btn gap-right toggled"
                    if self.file_mode == "all"
                    else "toggle-btn gap-right"
                )
                yield NeonButton(
                    label=self._set_select_files_btn_label(), id="select-files-btn",
                    classes="toggle-btn toggled gap-left"
                    if self.file_mode == "select"
                    else "toggle-btn gap-left"
                )
            yield NeonButton("Start Processing", id="start-btn", classes="extra-wide-btn", variant="primary")

    @staticmethod
    def _highlight_toggled_text(text: str) -> str:
        return f"\\[ {text} ]"

    def _set_all_files_btn_label(self) -> str:
        """Returns the label for the 'all-files-btn' button based on if it's toggled."""
        if self.file_mode == "all":
            return self._highlight_toggled_text("All Files in Dir")
        return "All Files in Dir"

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

    # FIXME: Make this a damn switch
    async def on_button_pressed(self, event: NeonButton.Pressed) -> None:
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
        # TODO: Implement these
        elif event.button.id == "save-defaults-btn":
            ...
        elif event.button.id == "restore-defaults-btn":
            ...
        elif event.button.id == "reset-defaults-btn":
            ...

    # handle reset

    async def on_select_changed(self, event: Select.Changed) -> None:
        if event.select.id == "bg-select":
            self.background_color = str(event.value)

    def _update_path_display(self) -> None:
        path_btn = self.query_one("#path-btn", NeonButton)
        path = self.selected_path.as_posix()
        path_btn.label = path

    def _update_file_mode_buttons(self) -> None:
        all_btn = self.query_one("#all-files-btn", NeonButton)
        sel_btn = self.query_one("#select-files-btn", NeonButton)
        all_btn.set_class(self.file_mode == "all", "toggled")
        sel_btn.set_class(self.file_mode == "select", "toggled")
        sel_btn.label = self._set_select_files_btn_label()

    def _update_numbers(self) -> None:
        self.query_one("#pad-left", Input).value = str(self.img_padding_left)
        self.query_one("#pad-right", Input).value = str(self.img_padding_right)
        self.query_one("#pad-top", Input).value = str(self.img_padding_top)
        self.query_one("#pad-bottom", Input).value = str(self.img_padding_bottom)

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

    def on_switch_button_changed(self, event: Toggle.Changed) -> None:
        """Handler for the custom message posted by the SwitchButton."""
        if event.ref.id == "split-image-toggle":
            self.split_image_active = event.active
            self.log(f"Split Image active state set to: {self.split_image_active}")
            event.stop()

    def _emit_settings_and_close(self) -> None:
        settings = {
            "path": str(self.selected_path),
            "files": self.selected_files if self.file_mode == "select" and self.selected_files else "ALL",
            "background_color": self.background_color,
            "split_wide_images": self.split_image_active,
            "padding": {
                "left": self.img_padding_left,
                "right": self.img_padding_right,
                "top": self.img_padding_top,
                "bottom": self.img_padding_bottom,
            },
        }
        self.dismiss(json.dumps(settings))
