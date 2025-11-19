import pyperclip
from textual import on
from textual.containers import Horizontal
from textual.message import Message
from textual.widget import Widget
from textual.widgets import Log

# Assuming MinimalButton is in this location
from textual_neon.widgets.minimal_button import MinimalButton


class AppLogWrite(Message):
    """
    A custom message to send a log string to the AppLevelLog widget
    from anywhere in the application.
    """
    def __init__(self, message: str, severity: str = "info") -> None:
        """
        Initializes the LogEvent.

        Args:
            message: The string content of the log.
            severity: The severity level (e.g., "info", "error").
        """
        self.message = message
        self.severity = severity
        super().__init__()


class AppLevelLog(Widget):
    """
    An enhanced, standalone Log widget that persists its history at the App level.
    All instances of AppLevelLog will share and display the same log history.

    It listens for `AppLogWrite` messages to write new lines and uses the `ensure_history` static method
    to guarantee the app-level log_history list exists.
    """
    DEFAULT_CSS = """
    AppLevelLog {
        Horizontal#log-controls-row {
            width: 100%;
            height: 1 !important;
            margin: 1 0 0 1 !important;
            padding: 0 !important;
            border: none !important;
            align: left middle !important;

            & > MinimalButton {
                margin: 0 1 0 0 !important;
            }
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
            *,
            show_copy_button: bool = True,
            show_clear_button: bool = True,
            copy_button_label: str = "Copy Logs",
            clear_button_label: str = "Clear Logs",
            **kwargs,
    ) -> None:
        """
        Initializes the AppLevelLog.
        """
        super().__init__(**kwargs)
        self._show_copy_button = show_copy_button
        self._show_clear_button = show_clear_button
        self._copy_button_label = copy_button_label
        self._clear_button_label = clear_button_label

        self.ensure_history()

    def compose(self):
        with Horizontal(id="log-controls-row"):
            yield MinimalButton(
                self._copy_button_label, id="copy-logs-btn", variant="primary"
            )
            yield MinimalButton(
                self._clear_button_label, id="clear-logs-btn", variant="primary"
            )
        yield Log(id="log")

    def ensure_history(self) -> list[str]:
        """
        Ensures the app has a 'log_history' attribute that is a list.
        """
        if hasattr(self.app, "log_history"):
            if not isinstance(self.app.log_history, list):
                raise AttributeError(
                    f"App must have the 'log_history' attribute set to a list. "
                    f"Different type detected: {type(self.app.log_history)}"
                )
            else:
                return self.app.log_history
        # noinspection PyTypeHints
        self.app.log_history: list[str] = []
        return self.app.log_history

    def on_mount(self) -> None:
        """
        Called when the widget is mounted.
        Sets button visibility and populates the log with persistent history.
        """
        self.query_one("#copy-logs-btn", MinimalButton).visible = self._show_copy_button
        self.query_one("#clear-logs-btn", MinimalButton).visible = self._show_clear_button

        log = self.query_one(Log)
        log_history = self.ensure_history()
        for line in log_history:
            log.write_line(line)
        log.scroll_end(animate=False)

    def info(self, content: str) -> None:
        """Writes in the log with the 'info' severity."""
        self.post_message(AppLogWrite(content, severity="info"))

    def warning(self, content: str) -> None:
        """Writes in the log with the 'warning' severity."""
        self.post_message(AppLogWrite(content, severity="warning"))

    def error(self, content: str) -> None:
        """Writes in the log with the 'error' severity."""
        self.post_message(AppLogWrite(content, severity="error"))

    def write_line(self, content: str) -> None:
        """
        Writes the line to the log AND appends it to the app's persistent history.
        """
        self.post_message(AppLogWrite(content, severity="info"))

    def write(self, content: str) -> None:
        """
        Writes the content to the log AND appends it to the app's persistent history.
        """
        self.post_message(AppLogWrite(content, severity="info"))

    @on(MinimalButton.Pressed, "#clear-logs-btn")
    def clear_logs(self, event: MinimalButton.Pressed) -> None:
        """
        Clears the on-screen log AND the app's persistent history.
        """
        event.stop()
        self.query_one(Log).clear()
        self.screen.notify("Logs cleared.")
        log_history = self.ensure_history()
        log_history.clear()

    @on(MinimalButton.Pressed, "#copy-logs-btn")
    def copy_logs(self, event: MinimalButton.Pressed) -> None:
        """
        Copies from the persistent history, ensuring all logs are copied.
        """
        event.stop()
        log_history = self.ensure_history()
        if not log_history:
            self.screen.notify("There are no logs to copy.", severity="warning")
            return

        all_text = "\n".join(log_history)

        try:
            pyperclip.copy(all_text)
            self.screen.notify("All logs have been copied to clipboard!")
        except Exception as e:
            self.screen.notify(f"{e}", title="Clipboard Error", severity="error")

    @on(AppLogWrite)
    def on_log_event(self, event: AppLogWrite) -> None:
        """
        Listens for the custom AppLogWrite message and writes to the log.
        """
        event.stop()
        log_line = f"[{event.severity.upper()}]: {event.message}"

        # Write directly to the Log widget to prevent recursion
        log_widget = self.query_one(Log)
        log_widget.write_line(log_line)

        log_history = self.ensure_history()
        log_history.append(log_line)

        log_widget.scroll_end(animate=True)