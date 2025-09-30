from pathlib import Path
from typing import Callable, Any
from textual import work
from textual.app import App
from textual.events import Resize
from textual.theme import Theme
from .screen_size import ScreenSize
from .screens.launch import LaunchScreen
from .screens.too_small import TooSmallScreen
from .state_machine import StateMachine

class PanelizerTUI(App[Any]):
    CSS_PATH = ["./css/globals.tcss"]
    TITLE = "Panelizer"
    SUB_TITLE = "Batch-fit your images onto single-color backgrounds"
    MIN_ROWS: int = 28
    MIN_COLS: int = 50
    SCREENS = {
        "launch": LaunchScreen,
        "too_small": TooSmallScreen,
    }
    DEFAULT_THEME = Theme(
        name="default",
        primary="#88c0d0",
        secondary="#81a1c1",
        accent="#b48ead",
        foreground="#d8dee9",
        background="#1e1e1e",
        success="#a3be8c",
        warning="#ebcb8b",
        error="#ea4b4b",
        surface="#3b4252",
        panel="#292f3a",
        dark=True,
        variables={
            "block-cursor-text-style": "none",
            "footer-key-foreground": "#88c0d0",
        },
    )
    def __init__(self) -> None:
        super().__init__()
        self.set_themes()
        self.launch_started = False
        self.too_small_modal_open = False
        self.selected_input_dir: Path | None = None
        self.state_machine = StateMachine(ui=self)
        self.screen_size = ScreenSize(ui=self)

    async def on_resize(self, event: Resize) -> None:
        await self.screen_size.handle_on_resize(event.size.width, event.size.height)

    def set_themes(self) -> None:
        """Registers the default theme and sets it as the current theme."""
        for light_theme in ("textual-light", "catppuccin-latte", "solarized-lite"):
            self.unregister_theme(light_theme)
        self.register_theme(self.DEFAULT_THEME)
        self.theme = "default"

    @work
    async def run_state_machine(self) -> None:
        """
        Runs the main state machine loop.
        Each state's name is used to look up the next state.
        """
        state_map: dict[str, Callable] = {
            "launch": self.launch_screen_state,
            # "other": self.other_state_func,
        }
        state_name: str | None = "launch"
        args = ()
        while state_name is not None:
            state_func = state_map.get(state_name)
            if state_func is None:
                break
            state_name, args = await state_func(*args)
        self.exit(args[0] if args else None)

    async def launch_screen_state(self) -> tuple[str | None, tuple]:
        """
        Presents the LaunchScreen and determines the next state.
        For now, always exits after completion.
        """
        path = await self.push_screen_wait("launch")
        if isinstance(path, Path) and path.exists():
            # In the future: return ("next_state_name", (path,))
            return None, (path,)
        return None, (path,)
