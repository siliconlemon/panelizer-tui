from typing import Any

from textual.app import ComposeResult
from textual.binding import Binding
from textual.screen import ModalScreen
from textual_fspicker.base_dialog import Dialog


class NeonDialog(ModalScreen[Any]):
    """
    A modal screen that uses the Dialog class from textual-fspicker as a base container.

    Note: Use this to define new dialogs in a simple manner. To address the size of the container,
    use NeonDialog > Dialog.
    """
    DEFAULT_CSS = """
    NeonDialog {
        align: center middle;
    
        Dialog {
            width: 80%;
            height: 80%;
            border: $border;
            background: $panel;
            border-title-color: $text;
            border-title-background: $panel;
            border-subtitle-color: $text;
            border-subtitle-background: $error;
    
            OptionList, OptionList:focus {
                background: $panel;
                background-tint: $panel;
            }
        }
    }
    """

    BINDINGS = [
        Binding("escape", "dismiss(None)", show=False),
    ]

    def __init__(self, title: str = "") -> None:
        super().__init__()
        self._title = title

    def compose(self) -> ComposeResult:
        dialog = Dialog(id="dialog")
        dialog.border_title = self._title
        yield dialog

