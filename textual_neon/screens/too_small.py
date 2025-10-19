from importlib import resources
from typing import TYPE_CHECKING

from textual.app import ComposeResult
from textual.containers import VerticalGroup
from textual.css.query import NoMatches
from textual.events import Resize
from textual.screen import ModalScreen
from textual.widgets import Label

if TYPE_CHECKING:
    from ..app import NeonApp


class TooSmallScreen(ModalScreen[None]):
    MODAL = True
    DEFAULT_CSS = """
    TooSmallScreen {
        width: 100%;
        height: 100%;
        dock: left;
        background: $background;
    
        #msg_group {
        width: 100%;
        height: 7;
        dock: top;
        align: left top;
        background: $background;
        border: round $error;
        padding: 1 2;
        margin: 1;
        }
    
        #msg_err {
            color: $error-lighten-1;
            text-style: bold;
            margin: 0;
        }
    
        #msg_size {
            color: $text;
            text-style: bold;
            margin: 0;
        }
    }
    """

    def __init__(self, min_height, min_width, width=None, height=None, **kwargs):
        super().__init__(**kwargs)
        self.min_height = min_height
        self.min_width = min_width
        self._pending_width = width
        self._pending_height = height

    def on_mount(self):
        """Updates the labels with the current terminal size when the screen is mounted."""
        self._update_labels()

    def on_show(self):
        """Updates the labels when the screen becomes visible."""
        self._update_labels()

    def on_resize(self, event: Resize) -> None:
        """Handles terminal resize events and updates the modal labels accordingly."""
        self.set_size(event.size.width, event.size.height)

    def compose(self) -> ComposeResult:
        with VerticalGroup(id="msg_group"):
            yield Label("Current window size is too small", id="msg_err", markup=True)
            yield Label("Awaiting live update values", id="msg_size", markup=True)

    def set_size(self, width, height):
        """Sets the current terminal size for display and updates the labels if mounted."""
        self._pending_width = width
        self._pending_height = height
        if self.is_mounted:
            self._update_labels()

    def _update_labels(self):
        """Updates the error and size labels displayed in the modal."""
        width = self._pending_width or 0
        height = self._pending_height or 0
        try:
            msg_err = self.query_one("#msg_err", expect_type=Label)
            msg_size = self.query_one("#msg_size", expect_type=Label)
            msg_err.update(
                f"Please, resize to at least {self.min_width} × {self.min_height}\n"
            )
            msg_size.update(
                f"Current size: {width} × {height}"
            )
        except NoMatches:
            pass


class ScreenSize:
    """
    Handles screen size checks and the 'too small' modal for a Textual app.
    Extends textual's App functionality with a parent reference.
    """

    def __init__(self, *, app: "NeonApp") -> None:
        self.app = app

    async def show_too_small_modal(self) -> None:
        """Displays the 'TooSmallScreen' modal if it is not already open."""
        if not self.app.too_small_modal_open:
            self.app.too_small_modal_open = True
            await self.app.push_screen(
                self.app.SCREENS["too_small"](
                    self.app.MIN_ROWS, self.app.MIN_COLS, width=self.app.size.width, height=self.app.size.height
                )
            )

    async def close_too_small_modal(self) -> None:
        """Closes the 'TooSmallScreen' modal if it is open."""
        if self.app.too_small_modal_open:
            await self.app.pop_screen()
            self.app.too_small_modal_open = False

    async def handle_on_resize(self, width: int, height: int) -> None:
        """
        Shows or hides the 'too small' modal based on terminal dimensions.
        Runs the main state machine if the size permits, and it has not yet started.
        """
        if height < self.app.MIN_ROWS or width < self.app.MIN_COLS:
            if not self.app.too_small_modal_open:
                await self.show_too_small_modal()
        else:
            if self.app.too_small_modal_open:
                await self.close_too_small_modal()
            if not self.app.app_started:
                self.app.app_started = True
                self.app.run_state_machine()