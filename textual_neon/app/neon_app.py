import json
from importlib import resources
from typing import Any

from textual import work
from textual.app import App
from textual.binding import Binding
from textual.events import Resize
from textual.theme import Theme
# noinspection PyProtectedMember
from textual.widgets._toggle_button import ToggleButton
from typing_extensions import override

from textual_neon.app.state_machine import StateMachine
from textual_neon.screens.too_small import TooSmallScreen

NOT_REGISTERED_MSG = """
|
|   To use NeonApp, first register your screens and data exchanges in self.state_machine.
|
|   Example:
|   
|   YourApp(NeonApp):
|       SCREENS = {
|           "launch": LaunchScreen,
|           "home": HomeScreen,
|       }
|       def __init__(self) -> None:
|           super().__init__()
|           self.state_machine.register(
|               "launch",
|               screen="launch",
|               next_state="home",
|               validate=lambda result: result is True,
|               data_from_result=lambda result: (),
|           )
|
"""

class NeonApp(App[Any]):
    """
    A base class for textual_neon apps, ensuring basic setup, propper screen size with default values
    and the absense of light themes.
    """
    CSS_PATH = [resources.files("textual_neon.css").joinpath("globals.tcss")]
    MIN_ROWS: int = 32
    MIN_COLS: int = 90
    SCREENS = {}
    BINDINGS = [
        Binding("right", "focus_next", "Next", show=False),
        Binding("left", "focus_previous", "Previous", show=False),
    ]
    DEFAULT_CSS = """
    Header {
        max-height: 1;
        background: transparent !important;
    }
    HeaderIcon {
        color: $foreground 50%;
    }
    CommandPalette {
        SearchIcon {
            display: none;
        }
        Vertical#--container {
            height: auto;
            background: $panel;
            max-width: 80;
            margin-top: 6;
            padding: 0;
            visibility: visible;
        }
        Horizontal#--input {
            max-height: 3;
            margin: 0;
            border-top: round $foreground 70%;
            border-bottom: none !important;
            border-left: round $foreground 70%;
            border-right: round $foreground 70%;
            visibility: visible;
        }
        Vertical#--results {
            margin: 0;
            padding: 0;
            border-bottom: round $foreground 70%;
            border-left: round $foreground 70%;
            border-right: round $foreground 70%;
        }
    }
    CommandInput {
        border: none !important;
        margin: 0;
        padding: 0;
        margin-left: 1;
    }
    CommandList {
        border: none !important;
        margin: 0;
        & > .option-list--option {
            padding: 0 1 0 1 !important;
            color: $text !important;
        }
        & > .option-list--option-highlighted {
            color: $text !important;
            background: $primary 50% !important;
        }
        &:focus {
            background-tint: $foreground 5%;
            & > .option-list--option-highlighted {
                color: $text !important;
                background: $primary 50% !important;
            }
        }
    }
    """
    DEFAULT_THEME = Theme(
        name="default",
        primary="#26d889",
        secondary="#98a1a5",
        accent="#23d4c9",
        foreground="#c0c5cd",
        background="#1e1e1e",
        success="#5da643",
        warning="#eba254",
        error="#ff4f68",
        surface="#3b4252",
        panel="#17171a",
        dark=True,
        variables={
            "block-cursor-text-style": "none",
        },
    )

    GREEN = "\033[92m"
    RESET = "\033[0m"

    def __init__(self) -> None:
        """Ensures that the TooSmallScreen is registered and sets up the StateMachine."""
        super().__init__()
        self.set_themes()
        self.app_started = False
        self.too_small_modal_open = False
        self.SCREENS.update({"too_small": TooSmallScreen})
        self.state_machine = StateMachine(app=self)
        # Overrides the default toggle button inner icon for more clarity
        ToggleButton.BUTTON_INNER = "●"

    def _register_defaults(self) -> None:
        """
        Sets app-wide definitions for all default values for the app.
        These are the "factory settings."

        Usage:
        ::
            # Inside __init__
            def __init__(self) -> None:
                super().__init__()
                self.settings = Settings(config_dir=Path("./settings"))
                self._register_defaults()
                self.settings.load()
                self._check_saved_theme()
            ...
            # Lower down
            @override
            def _register_defaults(self) -> None:
                s = self.settings
                s.register_default("theme", "default")
                s.register_default("start_dir", Paths.documents().as_posix())
                s.register_default("allowed_extensions", ["xls", "xlsx", "xlsm", "csv"])
        """
        pass

    async def on_mount(self) -> None:
        """Handles the initial size check on app startup."""
        width, height = self.size
        if height < self.MIN_ROWS or width < self.MIN_COLS:
            await self.show_too_small_modal(width, height)
        else:
            # Size is OK on startup, run the app.
            self.app_started = True
            self.run_state_machine()

    async def on_resize(self, event: Resize) -> None:
        """Handles all subsequent terminal resize events."""
        width, height = event.size

        if height < self.MIN_ROWS or width < self.MIN_COLS:
            # Screen is too small
            if not self.too_small_modal_open:
                await self.show_too_small_modal(width, height)
        else:
            # Screen is large enough
            if self.too_small_modal_open:
                await self.hide_too_small_modal()

            # If the app hasn't started yet (e.g., it started too small
            # and was just resized), start it now.
            if not self.app_started:
                self.app_started = True
                self.run_state_machine()

    async def show_too_small_modal(self, width: int, height: int) -> None:
        """Displays the 'TooSmallScreen' modal."""
        if not self.too_small_modal_open:
            self.too_small_modal_open = True
            await self.push_screen(
                self.SCREENS["too_small"](
                    self.MIN_ROWS, self.MIN_COLS, width=width, height=height
                )
            )

    async def hide_too_small_modal(self) -> None:
        """Closes the 'TooSmallScreen' modal."""
        if self.too_small_modal_open:
            if isinstance(self.screen, TooSmallScreen):
                await self.pop_screen()
            self.too_small_modal_open = False

    def set_themes(self) -> None:
        """Registers the default theme and removes all pre-built light themes."""
        for light_theme in ("textual-light", "catppuccin-latte", "solarized-light"):
            self.unregister_theme(light_theme)
        self.register_theme(self.DEFAULT_THEME)
        self.theme = "default"

    def watch_theme(self, old_theme: str, new_theme: str) -> None:
        """
        Saves the theme to settings if they have been set up for the instance.
        Use textual_neon.Settings to set up the settings object.
        """
        if new_theme in self.available_themes:
            if hasattr(self, "settings"):
                if not new_theme == self.settings.get("theme"):
                    self.settings.set("theme", new_theme)
                    self.settings.save()
        else:
            self.theme = old_theme

    def _check_saved_theme(self) -> None:
        """
        An init helper that checks if the app has a saved theme.
        If it does, that theme is set instead of the default.
        """
        if hasattr(self, "settings"):
            theme = self.settings.get("theme")
            if theme:
                self.theme = self.settings.get("theme")
                return
        self.theme = "default"

    @work
    async def run_state_machine(self) -> None:
        """Runs the app's state machine registered with data-driven states and transitions."""
        if not self.state_machine.registered:
            raise ValueError(
                NOT_REGISTERED_MSG
            )
        await self.state_machine.run(start_state="launch")

    @override
    def exit(self, result: Any | None = None, *, message: str | None = None, **kwargs) -> None:
        """
        Overrides the default exit to format the result as an exit message if no other message is provided.
        If the result is a valid JSON string, it will be pretty-printed.
        The output message uses the child app's TITLE to indicate its output.
        """
        if message is None and result is not None:
            if isinstance(result, str):
                try:
                    parsed_json = json.loads(result)
                    formatted_content = f"\n{json.dumps(parsed_json, indent=2)}"
                except json.JSONDecodeError:
                    formatted_content = f"\n{result}"
            elif isinstance(result, dict):
                formatted_content = f"\n{json.dumps(result, indent=2)}"
            else:
                formatted_content = f"\n{result}"

            message = f"{self.GREEN}│\n└─ {self.TITLE} Output: {formatted_content}{self.RESET}"

        super().exit(result, message=message, **kwargs)