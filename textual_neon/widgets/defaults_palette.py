from textual.app import ComposeResult
from textual.containers import Vertical, Horizontal
from textual.widget import Widget

from .inert_label import InertLabel
from ..widgets.defaults_button import DefaultsButton


class DefaultsPalette(Widget):
    """
    A widget with a label, a horizontal line, and three buttons: Save, Restore, Reset.

    Usage:
    ::
        # Inside your screen (using textual_neon.Settings)
        @on(DefaultsButton.Pressed, "#save-defaults-btn")
        async def save_defaults_button_pressed(self) -> None:
            self.settings.set("start_dir", self._selected_dir.as_posix())
            self.settings.save()
        ...
        @on(DefaultsButton.Pressed, "#restore-defaults-btn")
        def restore_defaults_button_pressed(self) -> None:
            self.settings.load()
            self._update_ui_from_preferences()
        ...
        @on(DefaultsButton.Pressed, "#reset-defaults-btn")
        def reset_defaults_button_pressed(self) -> None:
            self.settings.reset_all()
            self.settings.save()
            self._update_ui_from_preferences()
    """

    DEFAULT_CSS = """
    DefaultsPalette {
        height: 6;
        width: 100%;
        align-horizontal: center;

        .defaults-label {
            text-align: left;
            width: 100%;
            padding: 0;
            margin-left: 1;
        }

        .defaults-row {
            width: auto;
        }
    }
    """

    def __init__(
            self,
            *,
            save_btn_id: str = "defaults-save",
            restore_btn_id: str = "defaults-restore",
            reset_btn_id: str = "defaults-reset",
            widget_id: str | None = None,
            label: str = "Default Values",
            **kwargs,
    ):
        super().__init__(id=widget_id, **kwargs)
        self.label_text = label
        self.save_id = save_btn_id
        self.restore_id = restore_btn_id
        self.reset_id = reset_btn_id

    def compose(self) -> ComposeResult:
        with Vertical():
            yield InertLabel(self.label_text, classes="defaults-label")
            with Horizontal(classes="defaults-row"):
                yield DefaultsButton("Save", id=self.save_id, classes="gap-right", variant="save")
                yield DefaultsButton("Restore", id=self.restore_id, classes="gap-right", variant="restore")
                yield DefaultsButton("Reset", id=self.reset_id, variant="reset")
