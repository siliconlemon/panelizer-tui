from textual.app import ComposeResult
from textual.containers import VerticalGroup
from textual.css.query import NoMatches
from textual.events import Resize
from textual.screen import Screen
from textual.widgets import Static

class TooSmallScreen(Screen[None]):
    CSS_PATH = ["../css/too_small.tcss"]
    MODAL = True

    def __init__(self, min_height, min_width, width=None, height=None, **kwargs):
        super().__init__(**kwargs)
        self.min_height = min_height
        self.min_width = min_width
        self._pending_width = width
        self._pending_height = height

    def on_mount(self):
        self._update_labels()

    def on_show(self):
        self._update_labels()

    def on_resize(self, event: Resize) -> None:
        self.set_size(event.size.width, event.size.height)

    def set_size(self, width, height):
        self._pending_width = width
        self._pending_height = height
        if self.is_mounted:
            self._update_labels()

    def _update_labels(self):
        width = self._pending_width or 0
        height = self._pending_height or 0
        try:
            msg_err = self.query_one("#msg_err", expect_type=Static)
            msg_size = self.query_one("#msg_size", expect_type=Static)
            msg_err.update(
                f"Please, resize to at least {self.min_width} × {self.min_height}\n"
            )
            msg_size.update(
                f"Current size: {width} × {height}"
            )
        except NoMatches:
            pass

    def compose(self) -> ComposeResult:
        with VerticalGroup(id="msg_group"):
            yield Static("", id="msg_err", markup=True)
            yield Static("", id="msg_size", markup=True)
