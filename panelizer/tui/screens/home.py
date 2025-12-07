import asyncio
from pathlib import Path
from typing import Literal

from textual import on
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.validation import Integer
from textual.widgets import Input, Select

from textual_neon import SettingsPalette, CompleteInputGrid, CompleteSelect, \
    Toggle, NeonButton, DirSelectDialog, ChoicePalette, ListSelectDialog, \
    PathButton, Settings, ChoiceButton, SettingsButton, Paths, NeonInput, ScreenData, CompleteInput, NeonHeader, \
    NeonSelect


class HomeScreen(Screen[dict]):
    CSS_PATH = ["../css/home.tcss"]
    BINDINGS = []

    def __init__(self, data: ScreenData, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data = data
        self.settings = Settings.ensure(app=self.app)
        s = self.settings
        self.allowed_extensions: list[str] = s.get("allowed_extensions")
        self._selected_dir = Path(s.get("start_dir"))
        self.selected_files: list[str] = []
        self.file_mode: Literal["all", "select"] = "all"
        self.max_pad_percentage = 30

    def compose(self) -> ComposeResult:
        s = self.settings
        yield NeonHeader()
        with Vertical(id="home-container"):
            with Horizontal(id="path-row"):
                yield PathButton(self._selected_dir.as_posix(), id="path-btn")
            with Horizontal(id="main-row"):
                with Vertical(id="first-column"):
                    yield CompleteSelect(
                        select_id="layout-select",
                        label="Layout",
                        initial=s.get("layout"),
                        options=s.get("layout_options"),
                    )
                    with Horizontal(id="uniform-pad-container"):
                        yield CompleteInput(
                            id="img-pad-uniform",
                            label="All Sides (% of Height)",
                            value=s.get("img_pad_uniform"),
                            type_="number",
                            unit="%"
                        )
                    yield CompleteSelect(
                        select_id="uniform-orientation-select",
                        label="Border Orientation",
                        initial=s.get("uniform_border_orientation"),
                        options=s.get("uniform_border_orientation_options"),
                        id="uniform-orientation-wrapper"
                    )
                    yield CompleteInputGrid(
                        rows=2,
                        columns=2,
                        values=[
                            s.get("img_pad_left"),
                            s.get("img_pad_right"),
                            s.get("img_pad_top"),
                            s.get("img_pad_bottom")
                        ],
                        labels=["Left", "Right", "Top", "Bottom"],
                        input_ids=["pad-left", "pad-right", "pad-top", "pad-bottom"],
                        units=["%", "%", "%", "%"],
                        id="pad-grid"
                    )
                    yield CompleteSelect(
                        select_id="height-select",
                        label="Canvas Height",
                        initial=s.get("canvas_height"),
                        options=s.get("canvas_height_options"),
                    )
                    yield CompleteSelect(
                        select_id="ratio-select",
                        label="Aspect Ratio",
                        initial=s.get("canvas_ratio"),
                        options=s.get("canvas_ratio_options"),
                        id="ratio-wrapper"
                    )
                with Vertical(id="second-column"):
                    yield CompleteSelect(
                        select_id="bg-select",
                        label="Background Color",
                        initial=s.get("background_color"),
                        options=s.get("background_color_options"),
                    )
                    yield Toggle(
                        switch_id="split-wide-toggle-switch",
                        text="Split Wide Images",
                        is_active=s.get("split_wide_active"),
                        id="split-wide-toggle",
                    )
                    yield Toggle(
                        switch_id="stack-landscape-toggle-switch",
                        text="Stack Landscape Images",
                        is_active=s.get("stack_landscape_active"),
                        id="stack-landscape-toggle",
                    )
                    yield SettingsPalette(
                        save_btn_id="save-settings-btn",
                        restore_btn_id="restore-settings-btn",
                        reset_btn_id="reset-settings-btn",
                        label="Current Settings",
                        id="settings-widget",
                    )

            yield ChoicePalette(
                name="File Selection Mode",
                labels=["All Files in Dir", "Select Files"],
                actions=[None, None],
                default_idx=0,
                labels_when_selected=[
                    "All Files in Dir",
                    lambda: (self._make_select_files_label() if self.selected_files else "Select Files"),
                ],
                orientation="horizontal",
                id="file-mode-palette",
            )
            yield NeonButton("Start Processing", id="start-btn", classes="extra-wide-btn", variant="primary")

    async def on_mount(self) -> None:
        img_pad_validator = Integer(
            minimum=0,
            maximum=self.max_pad_percentage,
        )
        for input_id in ["#pad-left", "#pad-right", "#pad-top", "#pad-bottom"]:
            input_widget = self.query_one(input_id, Input)
            input_widget.validators.append(img_pad_validator)
        self.query_one("#img-pad-uniform", Input).validators.append(img_pad_validator)
        self._update_path_display()
        self._update_padding_inputs()
        current_layout = self.settings.get("layout")
        self._refresh_layout_inputs(current_layout)
        await self._select_all_files()

    def _refresh_layout_inputs(self, layout: str) -> None:
        """Toggles visibility between the grid and the uniform input container."""
        is_uniform = layout == "uniform"
        self.query_one("#uniform-pad-container").set_class(not is_uniform, "hidden")
        self.query_one("#uniform-orientation-wrapper").set_class(not is_uniform, "hidden")
        self.query_one("#pad-grid").set_class(is_uniform, "hidden")
        self.query_one("#ratio-select", NeonSelect).parent.parent.set_class(is_uniform, "hidden")
        self.query_one("#ratio-wrapper").set_class(is_uniform, "hidden")

    def _get_all_files_in_dir_blocking(self) -> list[Path]:
        """A blocking method to get all allowed files in the selected directory."""
        return list(Paths.all_files_in_dir(self._selected_dir, extensions=self.allowed_extensions))

    @on(PathButton.Pressed, "#path-btn")
    async def path_button_pressed(self) -> None:
        self.run_worker(self._select_dir_worker, exclusive=True)

    @on(NeonInput.Blurred)
    def input_blurred(self, event: Input.Submitted) -> None:
        mapping = {
            "pad-left": "img_pad_left",
            "pad-right": "img_pad_right",
            "pad-top": "img_pad_top",
            "pad-bottom": "img_pad_bottom",
            "img-pad-uniform": "img-pad-uniform",
        }

        if event.input.id in mapping:
            setting_key = mapping[event.input.id]
            try:
                old_val = int(self.settings.get(setting_key))
            except ValueError:
                old_val = 0

            try:
                val = int(event.value)
            except ValueError:
                self.notify(f"Invalid value for {event.input.id}", title="Invalid Input", severity="error")
                val = 0

            val = max(0, min(self.max_pad_percentage, val))

            if val != old_val:
                self.settings.set(setting_key, val)
            event.input.value = str(val)
            self._update_padding_inputs()

    @on(Select.Changed, "#bg-select")
    def bg_select_changed(self, event: Select.Changed) -> None:
        self.settings.set("background_color", str(event.value))

    @on(Select.Changed, "#layout-select")
    def layout_select_changed(self, event: Select.Changed) -> None:
        new_layout = str(event.value)
        self.settings.set("layout", new_layout)
        self._refresh_layout_inputs(new_layout)

    @on(Select.Changed, "#uniform-orientation-select")
    def uniform_orientation_changed(self, event: Select.Changed) -> None:
        self.settings.set("uniform_border_orientation", str(event.value))

    @on(Select.Changed, "#height-select")
    def height_select_changed(self, event: Select.Changed) -> None:
        self.settings.set("canvas_height", str(event.value))

    @on(Select.Changed, "#ratio-select")
    def ratio_select_changed(self, event: Select.Changed) -> None:
        self.settings.set("canvas_ratio", str(event.value))

    @on(Toggle.Changed, "#split-wide-toggle")
    def split_wide_toggle_changed(self, event: Toggle.Changed) -> None:
        self.settings.set("split_wide_active", event.active)

    @on(Toggle.Changed, "#stack-landscape-toggle")
    def stack_landscape_toggle_changed(self, event: Toggle.Changed) -> None:
        self.settings.set("stack_landscape_active", event.active)

    @on(SettingsButton.Pressed, "#save-settings-btn")
    async def save_defaults_button_pressed(self) -> None:
        self.settings.set("start_dir", self._selected_dir.as_posix())
        self.settings.save()
        self.notify("Preferences have been saved.", title="Preferences Saved", severity="information")

    @on(SettingsButton.Pressed, "#restore-settings-btn")
    def restore_defaults_button_pressed(self) -> None:
        self.settings.load()
        self._update_ui_from_preferences()
        self.notify("Preferences have been restored.", title="Preferences Restored", severity="information")

    @on(SettingsButton.Pressed, "#reset-defaults-btn")
    def reset_defaults_button_pressed(self) -> None:
        self.settings.reset_all()
        self.settings.save()
        self._update_ui_from_preferences()
        self.notify(
            "Preferences have been reset to factory defaults.\n"
            "Click 'Save' to overwrite your settings with these values.",
            title="Preferences Reset",
            severity="warning"
        )

    @on(ChoiceButton.Selected)
    async def file_mode_selected(self):
        palette = self.query_one("#file-mode-palette", ChoicePalette)
        idx = palette.selected_idx
        if idx == 0:
            await self._select_all_files()
        elif idx == 1:
            self._select_individual_files()

    @on(NeonButton.Pressed, "#start-btn")
    async def start_button_pressed(self) -> None:
        self._handle_dismiss()

    async def _select_files_worker(self) -> None:
        """A screen-level worker that pushes a file select dialog and updates the UI."""
        all_matching_files = await asyncio.to_thread(self._get_all_files_in_dir_blocking)
        files = list(map(self._file_path_to_tuple, all_matching_files))

        if not files:
            self.notify(
                f"No files with the allowed extensions ({', '.join(self.allowed_extensions)}) "
                f"found in dir {self._selected_dir.as_posix()}",
                severity="warning"
            )
            self.query_one("#file-mode-palette", ChoicePalette).select(0)
            await self._select_all_files()
            return
        dialog_title = f"Select Files ({", ".join(self.allowed_extensions)})"
        files_from_dialog = await self.app.push_screen_wait(
            ListSelectDialog(dialog_title, files)
        )
        if files_from_dialog is None:
            return
        self.selected_files = files_from_dialog
        if not self.selected_files:
            await self._select_all_files()
        self.query_one("#file-mode-palette", ChoicePalette).refresh_disp_state()

    async def _select_dir_worker(self) -> None:
        """A screen-level worker that pushes a dir select dialog and updates the UI."""
        new_dir = await self.app.push_screen_wait(DirSelectDialog(location=self._selected_dir))
        if new_dir:
            new_path = Path(new_dir)
            if new_path != self._selected_dir:
                self._selected_dir = new_path
                self._update_path_display()
        await self._select_all_files()

    def _update_ui_from_preferences(self) -> None:
        """Pulls all values from self.settings and updates the UI widgets."""
        s = self.settings
        self._selected_dir = Path(s.get("start_dir"))
        self._update_path_display()
        self._update_padding_inputs()
        bg_select = self.query_one("#bg-select", Select)
        bg_select.set_options(s.get("background_color_options"))
        bg_select.value = s.get("background_color")
        self.query_one("#split-wide-toggle", Toggle).is_active = s.get("split_wide_active")
        self.query_one("#stack-landscape-toggle", Toggle).is_active = s.get("stack_landscape_active")

    def _update_path_display(self) -> None:
        """Updates the PathButton label from the internal _selected_dir state."""
        path_btn = self.query_one("#path-btn", PathButton)
        path = self._selected_dir.as_posix()
        path_btn.label = path

    def _update_padding_inputs(self) -> None:
        """Updates padding input values by reading directly from settings."""
        s = self.settings
        self.query_one("#pad-left", Input).value = str(s.get("img_pad_left"))
        self.query_one("#pad-right", Input).value = str(s.get("img_pad_right"))
        self.query_one("#pad-top", Input).value = str(s.get("img_pad_top"))
        self.query_one("#pad-bottom", Input).value = str(s.get("img_pad_bottom"))
        self.query_one("#img-pad-uniform", Input).value = str(s.get("img_pad_uniform"))

    def _file_path_to_tuple(self, path: Path) -> tuple[str, str, bool]:
        """Formats a Path object into a tuple for the ListSelectDialog."""
        path_str = path.as_posix()
        is_selected = path_str in set(self.selected_files)
        return path.name, path_str, is_selected

    async def _select_all_files(self) -> None:
        """Sets the file mode to 'all' and populates selected_files with all valid files."""
        self.file_mode = "all"
        all_files = await asyncio.to_thread(self._get_all_files_in_dir_blocking)
        self.selected_files = [path.as_posix() for path in all_files]
        self.query_one("#file-mode-palette", ChoicePalette).select(0)

    def _select_individual_files(self) -> None:
        """Sets the file mode to 'select' and launches the file selection worker."""
        if self.file_mode == "all":
            self.selected_files = []
        self.file_mode = "select"
        self.run_worker(self._select_files_worker, exclusive=True)

    def _make_select_files_label(self) -> str:
        """Generates the label for the 'Select Files' button based on the current count."""
        count = len(self.selected_files)
        match count:
            case 0:
                return "Select Files"
            case 1:
                return f"{count} File Selected"
            case _:
                return f"{count} Files Selected"

    def _handle_dismiss(self) -> None:
        """Validates file selection and bundles all settings into a dict to dismiss the screen."""
        if not self.selected_files:
            self.notify(
                f"No files with the allowed extensions ({', '.join(self.allowed_extensions)})\n"
                f"found in dir {self._selected_dir.as_posix()}",
                title="No Files Selected",
                severity="error"
            )
            return

        s = self.settings
        layout = s.get("layout")

        if layout == "uniform":
            padding = {
                "uniform": s.get("img_pad_uniform"),
                "orientation": s.get("uniform_border_orientation")
            }
            canvas_ratio = None
        else:
            padding = {
                "left": s.get("img_pad_left"),
                "right": s.get("img_pad_right"),
                "top": s.get("img_pad_top"),
                "bottom": s.get("img_pad_bottom"),
            }
            canvas_ratio = s.get("canvas_ratio")

        settings = {
            "selected_dir": str(self._selected_dir),
            "selected_files": self.selected_files,
            "background_color": s.get("background_color"),
            "layout": layout,
            "canvas_height": int(s.get("canvas_height")),
            "canvas_ratio": canvas_ratio,
            "split_wide_images": s.get("split_wide_active"),
            "stack_landscape_images": s.get("stack_landscape_active"),
            "padding": padding,
        }
        self.dismiss(settings)
