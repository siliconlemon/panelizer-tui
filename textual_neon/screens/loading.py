import asyncio
from collections.abc import Callable
from email.header import Header

from textual import on
from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.screen import Screen
from textual.widgets import Digits, ProgressBar, LoadingIndicator, Log, Static, Header
from textual_fspicker.base_dialog import Dialog

from textual_neon.widgets.neon_button import NeonButton


class LoadingScreen(Screen):
    """
    A loading screen displaying progress and logs, centered on the screen.
    Uses the Digits, ProgressBar, LoadingIndicator, and Log widgets.
    """
    DEFAULT_CSS = """
    LoadingScreen {
        align: center middle;
        background: $background;

        Dialog#loading-container {
            align: center middle;
            width: 80%;
            max-width: 90;
            height: auto;
            padding: 1 2 1 2;
            color: $text;
            border: round $accent 50%;
            border-title-color: $text;
            background: transparent;

            Horizontal {
                height: auto;
                align: center middle;
                padding: 1;
                margin: 0 0 1 0;

                Digits {
                    width: 1fr;
                    margin: 0;
                    padding: 0;
                    border: none;
                }
                Digits#current {
                    text-align: right;
                }
                Digits#total {
                    text-align: left;
                }
                Static {
                    width: auto;
                    margin: 0 1 0 1;
                }
            }

            ProgressBar {
                width: 100%;
                height: auto;
                margin: 0 0 1 0;
                padding: 0 1 0 1;
                Bar {
                    width: 100%;
                }
                &.-complete {
                    margin: 0 0 3 0;
                }
            }

            LoadingIndicator {
                width: 100%;
                height: auto;
                margin-bottom: 1;
            }

            Log {
                width: 100%;
                height: 15;
                padding: 0 1 0 1;
                border: round $accent 50%;
                background: transparent;
                scrollbar-size-vertical: 0;
                scrollbar-size-horizontal: 0;
                &:focus {
                    background-tint: transparent;
                    border: round $accent;
                    &:hover {
                        border: round $accent 50%;
                    }
                }
                &:hover {
                    border: round $accent;
                }
            }
        }
        
        & > Horizontal {
            height: auto;
            width: 80%;
            max-width: 90;
            align: right middle;
        
            NeonButton#cancel {
                width: 20;
            }
        }
    }
    """

    def __init__(
            self,
            items: list | tuple,
            names: list[str] | tuple[str],
            function: Callable,
            title: str = "Loading",
            **kwargs
    ):
        super().__init__(**kwargs)
        self._title = title
        self._items = items
        self._names = names
        self._total = len(items)
        self._justified_digits: int = len(str(self._total))
        self._function = function
        self._results = []

    def compose(self) -> ComposeResult:
        """Create the child widgets for the loading screen."""
        yield Header(icon="●")
        with Dialog(id="loading-container"):
            with Horizontal():
                yield Digits("0".rjust(self._justified_digits, '0'), id="current")
                yield Static("  ╱\n ╱ \n╱  ")
                yield Digits(f"{self._total}".rjust(self._justified_digits, '0'), id="total")
            yield ProgressBar(self._total, show_bar=True, show_percentage=False, show_eta=False)
            yield LoadingIndicator()
            yield Log()
        with Horizontal():
            yield NeonButton("Cancel", variant="primary", id="cancel")

    async def on_mount(self) -> None:
        """Start the processing worker when the screen is mounted."""
        self.query_one(Dialog).border_title = self._title
        self.query_one(Log).write("Initializing...\n")
        self.run_worker(self.process_items, exclusive=False)

    @on(NeonButton.Pressed, "#cancel")
    def cancel_button_pressed(self) -> None:
        """Handle cancel button press."""
        # self.dismiss("home")
        self.dismiss(self._results)

    async def process_items(self) -> None:
        """The worker method to process items and update the UI."""
        log = self.query_one(Log)
        progress_bar = self.query_one(ProgressBar)
        current_digits = self.query_one("#current", Digits)
        loading_indicator = self.query_one(LoadingIndicator)

        if len(self._items) != len(self._names):
            log.write_line("Error: The number of items and names does not match!")
            log.write_line("\nAborting...")

        try:
            for i, item in enumerate(self._items):
                current_step = i + 1
                log.write_line(f"Processing [{current_step}/{self._total}]: {self._names[i][:50]}...")
                maybe_coroutine = self._function(item)
                if asyncio.iscoroutine(maybe_coroutine):
                    result = await maybe_coroutine
                else:
                    if i % 30 == 0:
                        await asyncio.sleep(0)
                    result = maybe_coroutine
                self._results.append(result)
                progress_bar.advance(1)
                current_digits.update(f"{current_step}".rjust(self._justified_digits, '0'))

            loading_indicator.display = False
            progress_bar.add_class("-complete")
            current_digits.update(
                f"{self._total}".rjust(self._justified_digits, '0')
            )
            log.write_line("\nProcessing complete!")

        except asyncio.CancelledError:
            log.write_line("\nProcessing canceled.")
