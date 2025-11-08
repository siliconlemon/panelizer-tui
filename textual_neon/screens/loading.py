import asyncio
from collections.abc import Callable
from email.header import Header

from textual import on
from textual.app import ComposeResult
from textual.containers import Horizontal, Container
from textual.css.query import NoMatches
from textual.screen import Screen
from textual.widgets import Digits, ProgressBar, LoadingIndicator, Header

from textual_neon.widgets.neon_log import NeonLog
from textual_neon.widgets.neon_header import NeonHeader
from textual_neon.widgets.neon_footer import  NeonFooter
from textual_neon.widgets.inert_label import InertLabel
from textual_neon.widgets.neon_button import NeonButton


class LoadingScreen(Screen):
    """
    A loading screen displaying progress and logs, centered on the screen.
    Uses the Digits, ProgressBar, LoadingIndicator, and NeonLog widgets.
    """
    DEFAULT_CSS = """
    LoadingScreen {
        align: center middle;
        background: $background;

        Container#loading-container {
            align: center middle;
            width: 80%;
            max-width: 90;
            height: auto;
            padding: 0 2 0 2;
            color: $foreground 70%;
            border: round $foreground 60%;
            border-title-color: $foreground 70%;
            background: transparent;

            Horizontal {
                height: auto;
                align: center middle;
                padding: 1;

                Digits {
                    width: 1fr;
                    margin: 0;
                    padding: 0;
                    border: none;
                }
                Digits#current {
                    color: $foreground;
                    text-align: right;
                }
                Digits#total {
                    color: $foreground;
                    text-align: left;
                }
                InertLabel#out-of {
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
                    margin: 0 0 2 0;
                }
            }
            LoadingIndicator {
                width: 100%;
                height: 1fr;
                margin-bottom: 0;
                height: 1 !important;
            }
            NeonLog {
                height: 14;
                width: 100%;
            }
        }

        & > Horizontal {
            height: auto;
            width: 80%;
            max-width: 90;
            align: right middle;
            
            NeonButton#continue {
                width: 20;
                margin-right: 2;
            }
            NeonButton#cancel {
                width: 20;
                margin-right: 1;
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
            continue_text: str = "Continue",
            cancel_text: str = "Cancel",
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
        self._finished = False
        self._continue_text = continue_text
        self._cancel_text = cancel_text

    def compose(self) -> ComposeResult:
        """Create the child widgets for the loading screen."""
        yield NeonHeader()
        with Container(id="loading-container"):
            with Horizontal():
                yield Digits("0".rjust(self._justified_digits, '0'), id="current")
                yield InertLabel("  ╱\n ╱ \n╱  ", id="out-of")
                yield Digits(f"{self._total}".rjust(self._justified_digits, '0'), id="total")
            yield ProgressBar(self._total, show_bar=True, show_percentage=False, show_eta=False)
            yield LoadingIndicator()
            yield NeonLog(show_clear_button=False)
        with Horizontal():
            yield NeonButton(self._continue_text, variant="primary", id="continue")
            yield NeonButton(self._cancel_text, variant="primary", id="cancel")

    async def on_mount(self) -> None:
        """Start the processing worker when the screen is mounted."""
        self.query_one("#loading-container", Container).border_title = self._title
        self.query_one(NeonLog).write("Initializing...\n")
        continue_button = self.query_one("#continue", NeonButton)
        continue_button.visible = False
        continue_button.disabled = True

        self.run_worker(self.process_items, exclusive=False)

    @on(NeonButton.Pressed, "#cancel")
    def cancel_button_pressed(self) -> None:
        """Handle cancel button press."""
        if self._finished:
            self.dismiss(("cancel", True))
        else:
            self.dismiss(("cancel", False))

    @on(NeonButton.Pressed, "#continue")
    def continue_button_pressed(self) -> None:
        """Handle the continued button press."""
        self.dismiss(("continue", True))

    async def process_items(self) -> None:
        """The worker method to process items and update the UI."""
        log = self.query_one(NeonLog)
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

            self._finished = True
            continue_button = self.query_one("#continue", NeonButton)
            continue_button.visible = True
            continue_button.disabled = False

        except asyncio.CancelledError:
            self.screen.notify("Loading screen has been abruptly closed.", severity="warning")