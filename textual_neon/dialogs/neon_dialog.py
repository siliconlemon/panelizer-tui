from typing import Any

from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.screen import ModalScreen
from textual_fspicker.base_dialog import Dialog

from textual_neon.widgets.neon_button import NeonButton


class NeonDialog(ModalScreen[Any]):
    """
    A modal screen that uses the Dialog class from textual-fspicker as a base container.

    Note: Use this to define new dialogs in a simple manner. To address the size of the container,
    use NeonDialog > Dialog. Make sure you follow the proper usage guidelines below.

    Usage:
    ::
        async def on_button_pressed(self, event: textual.widgets.Button.Pressed) -> None:
            match event.button.id:
                case "select-files-btn":
                    self.file_mode = "select"
                    self.run_worker(self._select_files_worker, exclusive=True)
                    event.stop()
        ...
        async def _select_files_worker(self) -> None:
            files = await self.app.push_screen_wait(ListSelectDialog())
            self.selected_files = files or []
        ...
    """
    DEFAULT_CSS = """
    NeonDialog {
        align: center middle;
    
        Dialog {
            width: 80%;
            height: 80%;
            border: round $foreground 60%;
            background: $panel;
            border-title-color: $foreground 70%;
            border-subtitle-color: $foreground 70%;
            border-title-background: transparent;
            border-subtitle-background: transparent;
    
            OptionList, OptionList:focus {
                background: $panel;
                background-tint: $panel;
            }
            
            NeonButton#close {
                color: $foreground 80%;
                border: round $foreground 70%;
            
                min-width: 5;
                max-width: 5;
                margin: 0 1 1 1;
                dock: right;
                
                &:hover {
                    color: $accent;
                    border: round $accent;
                }
                &:focus {
                    color: $accent;
                    border: round $accent;
                    &:hover {
                        color: $accent 70%;
                        border: round $accent 60%;
                    }
                }
                &.-active {
                    color: $accent 40%;
                    border: round $accent 30%;
                }
                &:disabled {
                    color: $foreground 40%;
                    border: round $foreground 30%;
                }
            }
        }
    }
    """

    BINDINGS = [
        Binding("escape", "dismiss(None)", show=False)
    ]

    def __init__(self, title: str = "", **kwargs) -> None:
        super().__init__()
        self._title = title

    def compose(self) -> ComposeResult:
        dialog = Dialog(id="dialog")
        dialog.border_title = self._title
        with dialog:
            yield NeonButton(" ✕ ", id="close")

    @on(NeonButton.Pressed, "#close")
    def handle_close(self) -> None:
        self.dismiss(None)