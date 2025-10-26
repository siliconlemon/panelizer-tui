from typing import Any, Iterable, Tuple

from textual import on
from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.widgets import SelectionList
from textual_fspicker.base_dialog import Dialog

from textual_neon.dialogs.neon_dialog import NeonDialog
from textual_neon.widgets.neon_button import NeonButton

SelectionItem = Tuple[str, Any] | Tuple[str, Any, bool]


class ListSelectDialog(NeonDialog):
    """
    A modal dialog for selecting one or more items from a list.

    Returns the list of selected values when "Select" is pressed,
    or None if closed.
    """
    DEFAULT_CSS = """
    ListSelectDialog {
        
        & > Dialog {
            layout: vertical;
            width: auto;
            height: auto;
            max-width: 80%;
            max-height: 80%;
        }
    
        & SelectionList {
            border: none;
            margin: 1 0 1 0;
            width: auto;
            height: auto;
            min-width: 50;
            min-height: 20;
            
            &:focus, &:focus-within {
                border: none;
            }
        }
    
        & Horizontal#dialog-buttons {
            dock: bottom;
            align: right bottom;
            height: auto;
            width: 100%;
            padding: 0 1 0 1;
        }
    
        & Horizontal#dialog-buttons > NeonButton {
            margin-left: 1;
            width: auto;
        }
    
        & NeonButton#close {
            dock: top;
            align: right top;
            margin: 0 0 0 1;
        }
    }
    """

    def __init__(self, items: Iterable[SelectionItem], title: str = "Select from list") -> None:
        super().__init__(title=title)
        self._items = items

    def compose(self) -> ComposeResult:
        """Create the dialog's widgets."""
        dialog = Dialog(id="dialog")
        dialog.border_title = self._title
        with dialog:
            yield SelectionList(*self._items, id="list-select")
            with Horizontal(id="dialog-buttons"):
                yield NeonButton("Confirm", variant="primary", id="confirm")
                yield NeonButton("Cancel", variant="primary", id="cancel")

    def on_mount(self) -> None:
        self.query_one(SelectionList).focus()

    @on(NeonButton.Pressed, "#confirm")
    def confirm_button_pressed(self) -> None:
        selection_list = self.query_one(SelectionList)
        self.dismiss(selection_list.selected)

    @on(NeonButton.Pressed, "#cancel")
    def cancel_button_pressed(self) -> None:
        self.dismiss(None)
