from collections.abc import Callable
from email.header import Header
from typing import Collection

from textual import on
from textual.app import ComposeResult
from textual.containers import Vertical, Horizontal
from textual.screen import Screen
from textual.widgets import Digits, ProgressBar, LoadingIndicator, Log, Static, Header

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

        Vertical#loading-container {
            align: center middle;
            width: 80%;
            max-width: 90;
            height: auto;
            padding: 1 2 1 2;
            border: round $accent 50%;
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
                    margin: 0 0 4 0;
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

    def __init__(self, name: str, items: Collection, function: Callable, **kwargs):
        super().__init__(name=name, **kwargs)
        self._items = items
        self._total = len(items)
        self._justified_digits: int = len(str(self._total))
        self._function = function
        self._results = []


    def compose(self) -> ComposeResult:
        """Create the child widgets for the loading screen."""
        yield Header(icon="●")
        with Vertical(id="loading-container"):
            with Horizontal():
                yield Digits("0".rjust(self._justified_digits, '0'), id="current")
                yield Static("  ╱\n ╱\n╱")
                yield Digits(f"{self._total}".rjust(self._justified_digits, '0'), id="total")
            yield ProgressBar(self._total, show_bar=True, show_percentage=False, show_eta=False)
            yield LoadingIndicator()
            yield Log()
        with Horizontal():
            yield NeonButton("Cancel", variant="primary", id="cancel")

    async def on_mount(self) -> None:
        """Start the processing worker when the screen is mounted."""
        self.query_one(Log).write("Initializing...\n")
        # Run the processing in a worker
        self.run_worker(self.process_items, exclusive=True)


    async def on_dismount(self) -> None:
        """Cancel all workers when the screen is dismounted."""
        self.workers.cancel_all()


    @on(NeonButton.Pressed, "#cancel")
    def cancel_button_pressed(self) -> None:
        """Handle cancel button press."""
        self.dismiss(self._results)


    async def process_items(self) -> None:
        """The worker method to process items and update the UI."""
        log = self.query_one(Log)
        progress_bar = self.query_one(ProgressBar)
        current_digits = self.query_one(Digits)
        loading_indicator = self.query_one(LoadingIndicator)

        try:
            for i, item in enumerate(self._items):
                current_step = i + 1

                log.write_line(f"Processing item {current_step}/{self._total}: {str(item)[:50]}...")

                result = self._function(item)

                self._results.append(result)
                # log.write_line(f"Completed item {current_step}/{self._total}.")

                progress_bar.advance(1)
                current_digits.update(f"{current_step}".rjust(self._justified_digits, '0'))

            loading_indicator.display = False
            progress_bar.add_class("-complete")
            current_digits.update(
                f"{self._total}".rjust(self._justified_digits, '0')
            )
            log.write_line("\nProcessing complete!")

        except Exception as e:
            log.write_line(f"\nError during processing:\n{e}")
            loading_indicator.display = False
            log.write_line("\nPress any key to return.")