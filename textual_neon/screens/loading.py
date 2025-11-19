import asyncio
import inspect
from typing import Any, Literal

from textual import on
from textual.app import ComposeResult
from textual.containers import Horizontal, Container
from textual.css.query import NoMatches
from textual.screen import Screen
from textual.widgets import Digits, ProgressBar, LoadingIndicator

from textual_neon.utils.errors import Errors
from textual_neon.utils.screen_data import ScreenData
from textual_neon.widgets.inert_label import InertLabel
from textual_neon.widgets.neon_button import NeonButton
from textual_neon.widgets.neon_header import NeonHeader
from textual_neon.widgets.neon_log import NeonLog


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
                &.-stopped {
                    margin: 0 0 2 0;
                    Bar > .bar--bar {
                        color: $error !important;
                    }
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

            NeonButton#stop {
                width: 20;
                margin-left: 1;
            }
            Container#spacer {
                width: 1fr;
                height: auto;
            }
            NeonButton#continue {
                width: 20;
                margin-right: 1;
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
            data: ScreenData,
            *,
            title: str = "Loading",
            continue_text: str = "Continue",
            cancel_text: str = "Cancel",
            stop_text: str = "Stop",
            allow_failures: bool = False,
            allow_duplicates: bool = False,
            show_clear_button: bool = False,
            **kwargs
    ):
        super().__init__(**kwargs)
        self.data = data
        self._items = data.payload
        self._names = data.payload_names
        self._function = data.function
        self._title = title
        self._total = len(self._items)
        self._justified_digits: int = len(str(self._total))

        self._results = []
        self._n_successes = 0
        self._n_failed = 0
        self._n_duplicates = 0

        self.allow_failures = allow_failures
        self.allow_duplicates = allow_duplicates

        self._success = False
        self._is_cancelled = False
        self._continue_text = continue_text
        self._cancel_text = cancel_text
        self._stop_text = stop_text
        self.show_clear_button = show_clear_button

        self._log: NeonLog | None = None
        self._progress_bar: ProgressBar | None = None
        self._current_digits: Digits | None = None
        self._loading_indicator: LoadingIndicator | None = None
        self._continue_button: NeonButton | None = None
        self._cancel_button: NeonButton | None = None
        self._stop_button: NeonButton | None = None

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
            yield NeonLog(show_clear_button=self.show_clear_button, id="log")
        with Horizontal():
            yield NeonButton(self._stop_text, variant="primary", id="stop")
            yield Container(id="spacer")
            yield NeonButton(self._continue_text, variant="primary", id="continue")
            yield NeonButton(self._cancel_text, variant="primary", id="cancel")

    async def on_mount(self) -> None:
        """Start the processing worker when the screen is mounted."""
        self.query_one("#loading-container", Container).border_title = self._title

        try:
            self._log = self.query_one(NeonLog)
            self._progress_bar = self.query_one(ProgressBar)
            self._current_digits = self.query_one("#current", Digits)
            self._loading_indicator = self.query_one(LoadingIndicator)
            self._continue_button = self.query_one("#continue", NeonButton)
            self._cancel_button = self.query_one("#cancel", NeonButton)
            self._stop_button = self.query_one("#stop", NeonButton)
        except NoMatches:
            await self.dismiss(("error", "Failed to mount loading screen widgets."))
            return

        self._log.write("Initializing...\n")
        self._continue_button.visible = False
        self._continue_button.disabled = True
        self.run_worker(self.process_items, exclusive=False)

    @on(NeonButton.Pressed, "#stop")
    def stop_button_pressed(self) -> None:
        """Handle stop button press. Hides a button and signals the worker to stop."""
        if self._stop_button:
            self._stop_button.display = False
            self._stop_button.disabled = True
        if self._loading_indicator:
            self._loading_indicator.display = False
        if self._progress_bar:
            self._progress_bar.add_class("-stopped")

        self._is_cancelled = True

    @on(NeonButton.Pressed, "#cancel")
    def cancel_button_pressed(self) -> None:
        """Handle cancel button press. Always dismisses with a 'cancel' status and no data."""
        self._is_cancelled = True
        self.dismiss(("cancel", None))

    @on(NeonButton.Pressed, "#continue")
    def continue_button_pressed(self) -> None:
        """Handle the continued button press. Dismisses with 'continue' and the processed data."""
        self.dismiss(("continue", self._results))

    async def process_items(self) -> None:
        """
        The main worker method to process all items and update the UI.
        Coordinates helper methods for setup, looping, and finalization.
        """
        if self._is_cancelled:
            return
        if not self._log:
            return
        if len(self._items) != len(self._names):
            self._log.write_line("Error: The number of items and names does not match!")
            self._log.write_line("\nAborting...")
            return

        action: Literal[
            "continue", "stop_processing_error", "stop_unexpected_error", "stop_cancelled"
        ] = "continue"

        try:
            is_async_func = inspect.iscoroutinefunction(self._function)
            for i, item in enumerate(self._items):
                if self._is_cancelled:
                    action = "stop_cancelled"
                    break

                current_step = i + 1
                item_name = self._names[i][:50]

                try:
                    self._log.write_line(f"Processing [{current_step}/{self._total}]: {item_name}...")
                except NoMatches:
                    action = "stop_unexpected_error"
                    break

                action = await self._process_single_item(
                    item, item_name, is_async_func
                )
                if action != "continue":
                    break

                try:
                    if self._progress_bar:
                        self._progress_bar.advance(1)
                    if self._current_digits:
                        self._current_digits.update(f"{current_step}".rjust(self._justified_digits, '0'))
                except NoMatches:
                    action = "stop_unexpected_error"
                    break

            self._finalize_processing(action)

        except asyncio.CancelledError:
            self._is_cancelled = True
            pass
        except NoMatches:
            self._is_cancelled = True
            pass

    # region Helper Methods

    async def _process_single_item(
            self, item: Any, item_name: str, is_async: bool
    ) -> Literal["continue", "stop_processing_error", "stop_unexpected_error", "stop_cancelled"]:
        """
        Processes a single item, handles results/exceptions, and updates counts.

        Args:
            item: The payload for the single item.
            item_name: The display name of the item for logging.
            is_async: Whether the function to run is asynchronous.

        Returns:
            A string literal indicating the processing outcome.
        """
        if not self._log:
            return "stop_unexpected_error"

        try:
            result: Any
            if is_async:
                result = await self._function(item)
            else:
                result = await asyncio.to_thread(self._function, item)

            if self._is_cancelled:
                return "stop_cancelled"

            if result is False:
                self._n_failed += 1
                self._log.write_line(f"VALIDATION FAILED: {item_name} (Skipping)")
            else:
                self._n_successes += 1
                self._results.append(result)

        except Errors.DuplicateError as e:
            if self._is_cancelled:
                return "stop_cancelled"
            self._n_duplicates += 1
            log_msg = f"DUPLICATE FOUND: {item_name}. {e}"
            self._log.write_line(f"{log_msg} Skipping, first instance kept.")

        except Errors.ProcessingError as e:
            if self._is_cancelled:
                return "stop_cancelled"
            self._n_failed += 1
            self._log.write_line(f"\nPROCESSING ERROR: {item_name} - {e}")
            return "stop_processing_error"

        except Exception as e:
            if self._is_cancelled:
                return "stop_cancelled"
            if "NoMatches" in str(e):
                return "stop_unexpected_error"
            self._n_failed += 1
            self._log.write_line(f"\nUNEXPECTED ERROR: {item_name} - {e}")
            return "stop_unexpected_error"

        return "continue"

    def _finalize_processing(
            self,
            action: Literal[
                "continue", "stop_processing_error", "stop_unexpected_error", "stop_cancelled"
            ]
    ) -> None:
        """
        Writes final summary logs and updates the UI state after the loop finishes.
        """
        if not all([
            self._log, self._progress_bar, self._current_digits,
            self._loading_indicator, self._continue_button,
            self._cancel_button, self._stop_button
        ]):
            return

        self._stop_button.display = False
        self._stop_button.disabled = True

        self._loading_indicator.display = False
        self._progress_bar.add_class("-complete")

        processing_stopped = (action != "continue")

        if processing_stopped:
            if action == "stop_processing_error":
                self._log.write_line("\nStopped due to a critical processing error.")
            elif action == "stop_unexpected_error":
                self._log.write_line("\nStopped due to an unexpected error.")
            elif action == "stop_cancelled":
                self._log.write_line("\nProcessing stopped by user.")

            self._log.write_line("Press 'Cancel' to return.")
            self._success = False
        else:
            self._current_digits.update(
                f"{self._total}".rjust(self._justified_digits, '0')
            )

            has_failures = self._n_failed > 0
            if not has_failures:
                self._log.write_line("\nAll items processed without failures!")
                self._success = True
            elif has_failures and self.allow_failures:
                self._log.write_line("\nProcessing complete, copy the logs to review failures.")
                self._success = True
            else:
                self._log.write_line("\nProcessing complete, with failures.")
                self._log.write_line("Press 'Cancel' to return.")
                self._success = False

        self._log.write_line(
            f"Successes: {self._n_successes}, Duplicates: {self._n_duplicates}, Failed: {self._n_failed}"
        )

        if self._success:
            self._continue_button.visible = True
            self._continue_button.disabled = False
            self._cancel_button.display = False
            self._cancel_button.disabled = True
        else:
            self._continue_button.visible = False
            self._continue_button.disabled = True
            self._cancel_button.visible = True
            self._cancel_button.disabled = False

    # endregion