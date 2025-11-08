import pyperclip
from click.termui import visible_prompt_func
from textual import on
from textual.containers import Horizontal
from textual.widget import Widget
from textual.widgets import Log

from textual_neon.widgets.minimal_button import MinimalButton


class NeonLog(Widget):
    DEFAULT_CSS = """
    NeonLog {
        Horizontal#log-controls-row {
            width: 100%;
            height: 1 !important;
            margin: 1 0 0 0 !important;
            padding: 0 0 0 0 !important;
            border: none !important;
            align: left middle !important;
        }
        
        Log#log {
            color: $text 70%;
            border: round $foreground 60%;
            text-style: none;
            width: 100%;
            height: 1fr;
            padding: 0 1 0 1;
            margin: 0 0 1 0;
            background: transparent;
            scrollbar-size-vertical: 0;
            scrollbar-size-horizontal: 0;
            &:focus {
                color: $text;
                border: round $foreground;
                background-tint: transparent;
                &:hover {
                    color: $text 70%;
                    border: round $foreground 60%;
                }
            }
            &:hover {
                color: $text;
                border: round $foreground;
            }
        }
    }
    """

    def __init__(
            self,
            show_copy_button: bool = True,
            show_clear_button: bool = True,
            **kwargs
    ) -> None:
        super().__init__(**kwargs)
        self._show_copy_button = show_copy_button
        self._show_clear_button = show_clear_button

    def compose(self):
        with Horizontal(id="log-controls-row"):
            yield MinimalButton("Copy Logs", id="copy-logs-btn", variant="primary")
            yield MinimalButton("Clear Logs", id="clear-logs-btn", variant="primary")
        yield Log(id="log")

    def on_mount(self) -> None:
        """Called when the widget is mounted."""
        self.query_one("#copy-logs-btn", MinimalButton).visible = self._show_copy_button
        self.query_one("#clear-logs-btn", MinimalButton).visible = self._show_clear_button

    def write_line(self, content: str) -> None:
        """A helper method to easily write a line to the internal Log widget."""
        self.query_one(Log).write_line(content)

    def write(self, content: str) -> None:
        """A helper method to easily write to the internal Log widget."""
        self.query_one(Log).write(content)

    @on(MinimalButton.Pressed, "#clear-logs-btn")
    def clear_logs(self) -> None:
        """Called when the 'Clear Logs' button is pressed."""
        self.query_one(Log).clear()
        self.notify("Logs cleared.")

    @on(MinimalButton.Pressed, "#copy-logs-btn")
    def copy_logs(self) -> None:
        """Called when the 'Copy Logs' button is pressed."""
        log = self.query_one(Log)
        all_text = "\n".join(str(line) for line in log.lines)

        if not all_text:
            self.notify("There is nothing to copy.", severity="warning")
            return

        try:
            pyperclip.copy(all_text)
            self.notify("Logs copied to clipboard!")
        except Exception as e:
            # This can fail on some systems (e.g., headless CI)
            self.notify(f"Clipboard error: {e}", severity="error")