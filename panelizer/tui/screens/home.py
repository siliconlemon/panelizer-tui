import json
from pathlib import Path
from typing import Literal

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical, Grid, Container
from textual.content import Content
from textual.events import Click, Enter, Leave
from textual.message import Message
from textual.reactive import reactive
from textual.screen import Screen
from textual.widget import Widget
from textual.widgets import Button, Input, Header, Static, Select, Switch, Label, Placeholder
from textual_fspicker import SelectDirectory

from ..dialogs.file_select import FileSelectDialog


# TODO: make this have variable rows (and maybe columns)
class GridInput(Grid):
    """
    A generic NxM grid widget with labels, suffixes and custom units.
    Each cell is defined by the one entry in the parallel lists:
    values, labels, suffixes and units.
    """
    DEFAULT_CSS = """
    GridInput {
        width: 100%;
        height: auto;
        margin-bottom: 1;
        layout: grid;
        
        .grid-cell {
            margin-left: 0;
            margin-right: 0;
        }
        .grid-row {
            layout: horizontal;
            align-vertical: middle;
            height: auto;
            width: 1fr;
            margin-bottom: 0;
            padding: 0;
        }
        .input {
            color: $text;
            width: 1fr;
            min-width: 10;
            min-height: 1;
            padding: 0 1;
            margin: 0;
        }
        .unit {
            width: 3;
            margin: 1 1 0 1;
            color: $accent;
        }
    }
    """

    def __init__(
        self,
        *,
        rows: int,
        columns: int,
        values: list[int],
        labels: list[str],
        input_ids: list[str],
        units: list[str],
        **kwargs
    ):
        super().__init__(**kwargs)
        self.rows = rows
        self.columns = columns
        self.ROW_HEIGHT = 4
        self.COLUMN_WIDTH = "1fr"

        expected = rows * columns
        n_values = len(values)
        n_labels = len(labels)
        n_suffixes = len(input_ids)
        n_units = len(units)

        if not (n_values == n_labels == n_suffixes == n_units):
            raise ValueError(
                f"GridInput: Mismatched argument lengths: "
                f"values={n_values}, labels={n_labels}, "
                f"suffixes={n_suffixes}, units={n_units}"
            )
        if n_values != expected:
            raise ValueError(
                f"GridInput: Given rows={rows} columns={columns} → {expected} cells, "
                f"but got {n_values} values (and similarly for other fields)."
            )

        self.values = values
        self.labels = labels
        self.input_ids = input_ids
        self.units = units

    async def on_mount(self):
        self.styles.height = self.rows * self.ROW_HEIGHT
        self.styles.grid_size_rows = self.rows
        self.styles.grid_size_columns = self.columns
        self.styles.grid_columns = [self.COLUMN_WIDTH] * self.columns
        self.styles.grid_rows = [self.ROW_HEIGHT] * self.rows


    def compose(self) -> ComposeResult:
        for idx in range(self.rows * self.columns):
            label = self.labels[idx]
            element_id = self.input_ids[idx]
            value = self.values[idx]
            unit = self.units[idx]
            with Vertical(classes="grid-cell"):
                yield Static(label, classes="input-label")
                with Horizontal(classes="grid-row"):
                    yield Input(str(value), id=element_id, classes="input", type="number")
                    yield Static(unit, classes="unit", disabled=True)


class SimpleSelect(Widget):
    """A widget for selecting the background color."""
    DEFAULT_CSS = """
        SimpleSelect {
            height: 5;
            margin-right: 1;
            border: none;
            
            .simple-select-input {
                min-height: 3;
                width: 1fr;
            }
            
            SelectCurrent {
                color: $text;
                border: none;
            }
            
            OptionList {
                margin-right: 3;
            }
        }
    """

    def __init__(self, *, label: str, initial_value: str, select_id: str, **kwargs):
        if select_id:
            self.select_id = select_id
        super().__init__(**kwargs)
        self.label = label
        self.initial_value = initial_value
        self.options = [
            ("White", "white"),
            ("Light Gray", "lightgray"),
            ("Dark Gray", "darkgray"),
            ("Black", "black"),
        ]

    label_hovered = reactive(False)

    def compose(self) -> ComposeResult:
        yield Static(self.label, classes="input-label", id="label")
        with Container(id="simple-select-container"):
            yield Select(
                id=self.select_id if self.select_id else None,
                classes="simple-select-input",
                compact=True,
                value=self.initial_value,
                allow_blank=False,
                options=self.options,
            )

    def on_enter(self) -> None:
        self.add_class("--hover")

    def on_leave(self) -> None:
        self.remove_class("--hover")


class SwitchButton(Widget):
    """A button emulation combining a Switch and a clickable label within a horizontal container."""

    class Changed(Message):
        """Posted when the switch's active state changes."""
        def __init__(self, switch_button: "SwitchButton", active: bool) -> None:
            super().__init__()
            self.switch_button = switch_button
            self.active = active

    is_active: reactive[bool] = reactive(False)

    DEFAULT_CSS = """
        SwitchButton {
            width: 100%;
            height: auto;
            padding: 0 1 0 0;
            margin-right: 5;
            layout: horizontal;
            text-align: center;
            border: round $secondary;
        
            &.--hover, &:focus-within {
                border: round $accent;
            }
            
            Label {
                width: 1fr;
                min-height: 1;
                text-align: center;
                padding: 0 1 0 1;
                text-style: bold;
                background: transparent;
                color: $text;
            }

            Switch {
                height: 1;
                padding: 0;
                margin: 0 2 0 1;
                background: transparent;
                border: none;
            }
            
            Switch:focus {
                background: $accent;
                border: none;
            }
        }
    """

    def __init__(
            self,
            *,
            text: str,
            is_active: bool = False,
            switch_id: str | None = None,
            text_id: str | None = None,
            **kwargs
    ):
        super().__init__(**kwargs)
        self._original_text = text
        self.text_id = text_id
        self.is_active = is_active

        self.switch = Switch(value=is_active, animate=False, id=switch_id if switch_id else self.id)
        self.text = Label(text, id=text_id)

    def compose(self) -> ComposeResult:
        yield self.switch
        yield self.text

    def on_switch_changed(self, event: Switch.Changed) -> None:
        event.stop()
        self.is_active = event.value
        local_is_active = event.value
        self.post_message(self.Changed(self, local_is_active))

    def on_click(self, event: Click) -> None:
        if event.widget is self.text or event.widget is self:
            event.stop()
            self.switch.toggle()
        elif event.widget is self.switch:
            event.stop()

    def on_enter(self) -> None:
        self.add_class("--hover")

    def on_leave(self) -> None:
        self.remove_class("--hover")


class Defaults(Widget):
    """A widget with a label, a horizontal line, and three buttons: Save, Restore, Reset."""

    DEFAULT_CSS = """
        Defaults {
            height: 6;
            width: 100%;
            margin-top: 1;
            align-horizontal: center;
            
            .defaults-label {
                text-align: left;
                width: 100%;
                padding: 0;
                color: $accent;
                text-style: bold;
            }
            
            .defaults-row {
                width: auto;
            }
            
            .defaults-btn {
                padding: 0;
                color: $text;
                border: round $secondary;
            }
            
            .defaults-btn:focus, .defaults-btn:hover {
                color: $text;
                border: round $accent;
            }
        }
    """

    def __init__(
        self,
        *,
        label: str = "Default Values",
        save_id: str = "defaults-save",
        restore_id: str = "defaults-restore",
        reset_id: str = "defaults-reset",
        widget_id: str | None = None,
        **kwargs,
    ):
        super().__init__(id=widget_id, **kwargs)
        self.label_text = label
        self.save_id = save_id
        self.restore_id = restore_id
        self.reset_id = reset_id

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Static(self.label_text, classes="defaults-label")
            with Horizontal(classes="defaults-row"):
                yield Button("Save", id=self.save_id, classes="defaults-btn gap-right save", variant="default")
                yield Button("Restore", id=self.restore_id, classes="defaults-btn gap-right restore", variant="primary")
                yield Button("Reset", id=self.reset_id, classes="defaults-btn reset", variant="error")



class HomeScreen(Screen[str]):
    CSS_PATH = ["../css/home.tcss"]
    BINDINGS = []

    def __init__(self, default_path: Path, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.selected_path: Path = default_path
        self.file_mode: Literal["all", "select"] = "all"
        self.selected_files: list[str] = []
        self.padding_left: int = 0
        self.padding_right: int = 0
        self.padding_top: int = 0
        self.padding_bottom: int = 0
        self.background_color: str = "white"
        self.split_image_active: bool = False

    def compose(self) -> ComposeResult:
        yield Header(icon="●")
        with Vertical(id="home-row"):
            with Horizontal(id="path-row"):
                yield Button(self.selected_path.as_posix(), id="path-btn", classes="extra-wide-btn")
            with Horizontal(id="main-row"):
                with Vertical(id="input-column"):

                    yield GridInput(
                        rows=2,
                        columns=2,
                        values=[self.padding_left, self.padding_right, self.padding_top, self.padding_bottom],
                        labels=["Left", "Right", "Top", "Bottom"],
                        input_ids=["pad-left", "pad-right", "pad-top", "pad-bottom"],
                        units=["%", "%", "%", "%"],
                        id="pad-grid"
                    )

                    yield SimpleSelect(
                        label="Background Color",
                        initial_value=self.background_color,
                        select_id="bg-select",
                    )

                    yield SwitchButton(
                        text="Split Wide Images",
                        is_active=self.split_image_active
                    )

                    yield Defaults(
                        label="Default Values",
                        save_id="save-defaults-btn",
                        restore_id="restore-defaults-btn",
                        reset_id="reset-defaults-btn",
                        widget_id="defaults-widget"
                    )

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

    def on_switch_button_changed(self, event: SwitchButton.Changed) -> None:
        """Handler for the custom message posted by the SwitchButton."""
        if event.switch_button.id == "split-image-toggle":
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
                "left": self.padding_left,
                "right": self.padding_right,
                "top": self.padding_top,
                "bottom": self.padding_bottom,
            },
        }
        self.dismiss(json.dumps(settings))
