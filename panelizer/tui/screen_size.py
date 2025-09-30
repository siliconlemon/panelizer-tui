from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from . import PanelizerTUI

class ScreenSize:
    """
    Handles screen size checks and the 'too small' modal for a Textual app.
    Extends the PanelizerTUI functionality with a parent reference.
    """

    def __init__(self, *, ui: "PanelizerTUI") -> None:
        self.ui = ui

    async def show_too_small_modal(self) -> None:
        """Displays the 'TooSmallScreen' modal if it is not already open."""
        if not self.ui.too_small_modal_open:
            self.ui.too_small_modal_open = True
            await self.ui.push_screen(
                self.ui.SCREENS["too_small"](
                    self.ui.MIN_ROWS, self.ui.MIN_COLS, width=self.ui.size.width, height=self.ui.size.height
                )
            )

    async def close_too_small_modal(self) -> None:
        """Closes the 'TooSmallScreen' modal if it is open."""
        if self.ui.too_small_modal_open:
            await self.ui.pop_screen()
            self.ui.too_small_modal_open = False

    async def handle_on_resize(self, width: int, height: int) -> None:
        """
        Shows or hides the 'too small' modal based on terminal dimensions.
        Runs the main state machine if the size permits, and it has not already started.
        """
        if height < self.ui.MIN_ROWS or width < self.ui.MIN_COLS:
            if not self.ui.too_small_modal_open:
                await self.show_too_small_modal()
        else:
            if self.ui.too_small_modal_open:
                await self.close_too_small_modal()
            if not self.ui.launch_started:
                self.ui.launch_started = True
                self.ui.run_state_machine()