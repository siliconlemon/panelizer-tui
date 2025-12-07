from textual.app import ComposeResult
from textual.containers import Vertical, Horizontal
from textual.widget import Widget

from textual_neon.widgets.inert_label import InertLabel
from textual_neon.widgets.settings_button import SettingsButton


class SettingsPalette(Widget):
    """
    A widget with a label, a horizontal line, and three buttons: Save, Restore, Reset.

    Usage:
    ::
        # Inside your screen (using textual_neon.Settings)
        @on(SettingsButton.Pressed, "#save-settings-btn")
        async def save_settings_button_pressed(self) -> None:
            self.settings.set("start_dir", self._selected_dir.as_posix())
            self.settings.save()
        ...
        @on(SettingsButton.Pressed, "#restore-settings-btn")
        def restore_settings_button_pressed(self) -> None:
            self.settings.load()
            self._update_ui_from_preferences()
        ...
        @on(SettingsButton.Pressed, "#reset-settings-btn")
        def reset_settings_button_pressed(self) -> None:
            self.settings.reset_all()
            self.settings.save()
            self._update_ui_from_preferences()
    """

    DEFAULT_CSS = """
    SettingsPalette {
        height: 6;
        width: 100%;
        align-horizontal: center;

        .settings-label {
            text-align: left;
            width: 100%;
            padding: 0;
            margin-left: 1;
        }

        .settings-row {
            width: auto;
        }
    }
    """

    def __init__(
            self,
            *,
            save_btn_id: str = "settings-save",
            restore_btn_id: str = "settings-restore",
            reset_btn_id: str = "settings-reset",
            label: str = "Current Settings",
            **kwargs,
    ):
        super().__init__(**kwargs)
        self.label_text = label
        self.save_id = save_btn_id
        self.restore_id = restore_btn_id
        self.reset_id = reset_btn_id

    def compose(self) -> ComposeResult:
        with Vertical():
            yield InertLabel(self.label_text, classes="settings-label")
            with Horizontal(classes="settings-row"):
                yield SettingsButton("Save", id=self.save_id, classes="gap-right", variant="save")
                yield SettingsButton("Restore", id=self.restore_id, classes="gap-right", variant="restore")
                yield SettingsButton("Reset", id=self.reset_id, variant="reset")
