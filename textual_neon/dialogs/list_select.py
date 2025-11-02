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
            border: round $foreground 80%;
            margin: 0;
            padding: 0;
            width: auto;
            height: auto;
            min-width: 50;
            min-height: 20;
            
            &:focus, &:hover, &:focus-within {
                border: round $foreground;
            }
        }
        
        & Horizontal#selection-buttons {
            dock: top;
            width: auto;
            height: auto;
            margin: 1 0 0 0;
            
            & > NeonButton {
                width: auto;
                border: none;
                margin: 0;
            }   
        }
    
        & Horizontal#dialog-buttons {
            dock: bottom;
            align: right bottom;
            height: auto;
            width: 100%;
            padding: 0 1 0 1;
            
            & > NeonButton {
                margin: 0 1 0 1;
                width: auto;
            }
        }
    }
    """

    def __init__(self, title: str, items: Iterable[SelectionItem]) -> None:
        super().__init__(title=title)
        self._items = items
        self._initial_selection = [
            item for item in items if len(item) > 2 and item[2]
        ]

    def compose(self) -> ComposeResult:
        """Create the dialog's widgets."""
        dialog = Dialog(id="dialog")
        dialog.border_title = self._title
        with dialog:
            with Horizontal(id="selection-buttons"):
                yield NeonButton("Select All", variant="primary", id="all")
                yield NeonButton("Select None", variant="primary", id="none")
            yield SelectionList(*self._items, id="list")
            with Horizontal(id="dialog-buttons"):
                yield NeonButton("Confirm", variant="primary", id="confirm")
                yield NeonButton("Cancel", variant="primary", id="cancel")

    @on(NeonButton.Pressed, "#all")
    def select_all_button_pressed(self) -> None:
        selection_list = self.query_one(SelectionList)
        selection_list.select_all()

    @on(NeonButton.Pressed, "#none")
    def select_none_button_pressed(self) -> None:
        selection_list = self.query_one(SelectionList)
        selection_list.deselect_all()

    @on(NeonButton.Pressed, "#confirm")
    def confirm_button_pressed(self) -> None:
        selection_list = self.query_one(SelectionList)
        self.dismiss(selection_list.selected)

    @on(NeonButton.Pressed, "#cancel")
    def cancel_button_pressed(self) -> None:
        self.dismiss(self._initial_selection)
