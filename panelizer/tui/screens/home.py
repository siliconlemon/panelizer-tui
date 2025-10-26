import json
from pathlib import Path
from typing import Literal

import textual
from textual import on
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Input, Header, Select
from textual.worker import Worker

from textual_neon import DefaultsPalette, CompleteInputGrid, CompleteSelect, \
    Toggle, NeonButton, DirSelectDialog, ChoicePalette, ChoiceButton, ListSelectDialog, \
    PathButton, Preferences


class HomeScreen(Screen[str]):
    CSS_PATH = ["../css/home.tcss"]
    BINDINGS = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.file_mode: Literal["all", "select"] = "all"
        self.selected_files: list[str] = []
        self.preferences = Preferences.ensure(app=self.app)
        p = self.preferences
        self._selected_dir = Path(p.get("start_dir"))
        self.img_pad_left = p.get("img_pad_left")
        self.img_pad_right = p.get("img_pad_right")
        self.img_pad_top = p.get("img_pad_top")
        self.img_pad_bottom = p.get("img_pad_bottom")
        self.background_color_options: list[tuple[str, str]] = p.get("background_color_options")
        self.background_color = p.get("background_color")
        self.split_wide_active = p.get("split_wide_active")
        self.stack_landscape_active = p.get("stack_landscape_active")
        self.split_wide_active: bool = p.get("split_wide_active")
        self.stack_landscape_active: bool = p.get("stack_landscape_active")

    def compose(self) -> ComposeResult:
        yield Header(icon="●")
        with Vertical(id="home-row"):
            with Horizontal(id="path-row"):
                yield PathButton(self._selected_dir.as_posix(), id="path-btn")
            with Horizontal(id="main-row"):
                with Vertical(id="first-column"):
                    yield CompleteInputGrid(
                        rows=2,
                        columns=2,
                        values=[self.img_pad_left, self.img_pad_right, self.img_pad_top, self.img_pad_bottom],
                        labels=["Left", "Right", "Top", "Bottom"],
                        input_ids=["pad-left", "pad-right", "pad-top", "pad-bottom"],
                        units=["%", "%", "%", "%"],
                        id="pad-grid"
                    )
                    yield Toggle(
                        switch_id="split-wide-toggle-switch",
                        text="Split Wide Images",
                        is_active=self.split_wide_active,
                        id="split-wide-toggle",
                    )
                    yield Toggle(
                        switch_id="stack-landscape-toggle-switch",
                        text="Stack Landscape Images",
                        is_active=self.stack_landscape_active,
                        id="stack-landscape-toggle",
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
            yield ChoicePalette(
                labels=["All Files in Dir", "Select Files"],
                actions=[None, None],
                default_idx=0,
                labels_when_selected=[
                    "All Files in Dir",
                    lambda: (self._select_files_label() if self.selected_files else "Select Files"),
                ],
                orientation="horizontal",
                id="file-mode-palette",
            )
            yield NeonButton("Start Processing", id="start-btn", classes="extra-wide-btn", variant="primary")


    async def on_mount(self) -> None:
        self._update_path_display()
        self._update_numbers()

    async def on_unmount(self) -> None:
        self.workers.cancel_all()

    async def on_button_pressed(self, event: textual.widgets.Button.Pressed) -> None:
        match event.button.id:
            case "path-btn":
                # FIXME: This breaks worker management
                self.run_worker(self._select_dir_worker, exclusive=True)
                event.stop()
            case "all-files-btn":
                self.file_mode = "all"
                self.selected_files = []
                event.stop()
            case "select-files-btn":
                self.file_mode = "select"
                self.run_worker(self._select_files_worker, exclusive=True)
                event.stop()
            case "start-btn":
                self._handle_dismiss()
                event.stop()
            case "save-defaults-btn":
                self._update_prefs_from_ui()
                self.preferences.save()
                self.notify("Defaults saved.", severity="information")
                event.stop()
            case "restore-defaults-btn":
                self.preferences.load()
                self._update_ui_from_prefs()
                self.notify("Defaults restored from file.", severity="information")
                event.stop()
            case "reset-defaults-btn":
                self.preferences.reset_all()
                self._update_ui_from_prefs()
                self.notify("Defaults reset to factory settings.", severity="warning")
                event.stop()

    def _update_ui_from_prefs(self) -> None:
        """Pulls all values from self.app.defaults and updates the UI widgets."""
        p = self.preferences
        self._selected_dir = Path(p.get("start_dir"))
        self.img_pad_left = p.get("img_pad_left")
        self.img_pad_right = p.get("img_pad_right")
        self.img_pad_top = p.get("img_pad_top")
        self.img_pad_bottom = p.get("img_pad_bottom")
        self.background_color_options = p.get("background_color_options")
        self.background_color = p.get("background_color")
        self.split_wide_active = p.get("split_wide_active")
        self.stack_landscape_active = p.get("stack_landscape_active")

        self._update_path_display()
        self._update_numbers()
        self.query_one("#bg-select", Select).set_options(self.background_color_options)
        self.query_one("#bg-select", Select).value = self.background_color
        self.query_one("#split-wide-toggle", Toggle).value = self.split_wide_active
        self.query_one("#stack-landscape-toggle", Toggle).value = self.stack_landscape_active

    def _update_prefs_from_ui(self) -> None:
        """Pushes current UI values into self.app.defaults (in memory)."""
        p = self.preferences
        p.set("start_dir", self._selected_dir.as_posix())
        p.set("img_pad_left", self.img_pad_left)
        p.set("img_pad_right", self.img_pad_right)
        p.set("img_pad_top", self.img_pad_top)
        p.set("img_pad_bottom", self.img_pad_bottom)
        p.set("background_color_options", self.background_color_options)
        p.set("background_color", self.background_color)
        p.set("split_wide_active", self.split_wide_active)
        p.set("stack_landscape_active", self.stack_landscape_active)

    async def _select_files_worker(self) -> None:
        files = await self.app.push_screen_wait(ListSelectDialog())
        self.selected_files = files or []

    async def _select_dir_worker(self) -> None:
        new_dir = await self.app.push_screen_wait(DirSelectDialog(location=self._selected_dir))
        if new_dir:
            self._selected_dir = Path(new_dir)
            self._update_path_display()

    async def on_select_changed(self, event: Select.Changed) -> None:
        if event.select.id == "bg-select":
            self.background_color = str(event.value)

    def _update_path_display(self) -> None:
        path_btn = self.query_one("#path-btn", NeonButton)
        path = self._selected_dir.as_posix()
        path_btn.label = path

    def _update_numbers(self) -> None:
        self.query_one("#pad-left", Input).value = str(self.img_pad_left)
        self.query_one("#pad-right", Input).value = str(self.img_pad_right)
        self.query_one("#pad-top", Input).value = str(self.img_pad_top)
        self.query_one("#pad-bottom", Input).value = str(self.img_pad_bottom)

    async def on_input_changed(self, event: Input.Changed) -> None:
        await self.on_input_submitted(Input.Submitted(event.input, event.value))

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        mapping = {
            "pad-left": "img_pad_left",
            "pad-right": "img_pad_right",
            "pad-top": "img_pad_top",
            "pad-bottom": "img_pad_bottom",
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
        match event.ref.id:
            case "split-wide-toggle":
                self.split_wide_active = event.active
                event.stop()
            case "stack-landscape-toggle":
                self.stack_landscape_active = event.active
                event.stop()

    @on(ChoiceButton.Selected)
    async def file_mode_changed(self):
        palette = self.query_one("#file-mode-palette", ChoicePalette)
        idx = palette.selected_idx
        if idx == 0:
            self.file_mode = "all"
            self.selected_files = []
        elif idx == 1:
            self.file_mode = "select"
            files = await self.app.push_screen_wait(ListSelectDialog())
            self.selected_files = files or []

    def _select_files_label(self) -> str:
        count = len(self.selected_files)
        if count == 0:
            return "Select Files"
        elif count == 1:
            return f"1 file: {Path(self.selected_files[0]).name}"
        elif count <= 3:
            file_names = ', '.join(Path(f).name for f in self.selected_files)
            return f"{count} Files: {file_names}"
        else:
            return f"{count} Files Selected"

    def _handle_dismiss(self) -> None:
        settings = {
            "path": str(self._selected_dir),
            "files": self.selected_files if self.file_mode == "select" and self.selected_files else "ALL",
            "background_color": self.background_color,
            "split_wide_images": self.split_wide_active,
            "stack_landscape_images": self.stack_landscape_active,
            "padding": {
                "left": self.img_pad_left,
                "right": self.img_pad_right,
                "top": self.img_pad_top,
                "bottom": self.img_pad_bottom,
            },
        }
        self.dismiss(json.dumps(settings))
