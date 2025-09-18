from textual.css.query import NoMatches
from textual.widget import Widget
from textual.containers import Container, VerticalGroup
from textual.widgets import Static, Label
from textual.reactive import reactive

class TooSmall(Widget):

    min_height = reactive(0)
    min_width = reactive(0)
    current_height = reactive(0)
    current_width = reactive(0)

    def __init__(self, min_height, min_width, **kwargs):
        super().__init__(**kwargs)
        self.min_height = min_height
        self.min_width = min_width

    def set_size(self, width, height):
        self.current_width = width
        self.current_height = height
        try:
            msg_err = self.query_one("#msg_err", expect_type=Static)
            msg_size = self.query_one("#msg_size", expect_type=Static)
            msg_err.update(self._render_msg_err())
            msg_size.update(self._render_msg_size())
        except NoMatches:
            pass

    def _render_msg_err(self):
        return (
            f"Please, resize to at least {self.min_width} × {self.min_height}\n"
        )

    def _render_msg_size(self):
        return (
            f"Current size: {self.current_width} × {self.current_height}"
        )

    def compose(self):
        with VerticalGroup(id="msg_group"):
            yield Static(self._render_msg_err(), id="msg_err", markup=True)
            yield Static(self._render_msg_size() , id="msg_size", markup=True)
