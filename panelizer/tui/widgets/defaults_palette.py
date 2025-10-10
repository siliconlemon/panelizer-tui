from textual.app import ComposeResult
from textual.containers import Vertical, Horizontal
from textual.widget import Widget
from textual.widgets import Static, Button


class DefaultsPalette(Widget):
    """A widget with a label, a horizontal line, and three buttons: Save, Restore, Reset."""

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

            .defaults-btn {
                padding: 0;
                color: $text;
                border: round $secondary;
            }

            .defaults-btn:focus, .defaults-btn:hover {
                color: $text;
                border: round $accent;
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
            yield Static(self.label_text, classes="defaults-label")
            with Horizontal(classes="defaults-row"):
                yield Button("Save", id=self.save_id, classes="defaults-btn gap-right save", variant="default")
                yield Button("Restore", id=self.restore_id, classes="defaults-btn gap-right restore", variant="primary")
                yield Button("Reset", id=self.reset_id, classes="defaults-btn reset", variant="error")
