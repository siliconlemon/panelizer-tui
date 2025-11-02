from textual.app import ComposeResult
from textual.containers import VerticalGroup
from textual.css.query import NoMatches
from textual.events import Resize
from textual.screen import ModalScreen
from textual.widgets import Label


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
            color: $text-error;
            text-style: bold;
            margin: 0;
        }

        #msg_size {
            color: $foreground;
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