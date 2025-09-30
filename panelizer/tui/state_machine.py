from pathlib import Path
from typing import TYPE_CHECKING, Callable, Awaitable, Any

if TYPE_CHECKING:
    from . import PanelizerTUI
    from .screens.home import HomeScreen

class StateMachine:
    """
    Handles UI workflow and screen transitions for the PanelizerTUI app.
    Each state is a coroutine referenced by its string key.
    Extends the PanelizerTUI functionality with a parent reference.
    """
    def __init__(self, *, ui: "PanelizerTUI"):
        """Initializes the state machine with UI reference and states."""
        self.ui = ui
        self.states: dict[str, Callable[..., Awaitable[tuple[str | None, tuple]]]] = {
            "launch": self.launch_screen_state,
            "home": self.home_screen_state,
        }

    async def run(self) -> None:
        """Runs the state machine loop until exit."""
        state_name: str | None = "launch"
        args = ()
        while state_name is not None:
            state_func = self.states.get(state_name)
            if state_func is None:
                break
            state_name, args = await state_func(*args)
        self.ui.exit(args[0] if args else None)

    async def launch_screen_state(self) -> tuple[str | None, tuple]:
        """
        Shows the LaunchScreen, collects a valid path,
        and transitions to home or exits.
        """
        path = await self.ui.push_screen_wait("launch")
        if isinstance(path, Path) and path.exists():
            return "home", (path,)
        return "launch", ()

    async def home_screen_state(self, path: Path) -> tuple[str | None, tuple]:
        """
        Shows the HomeScreen with the selected input path.
        Returns the settings as JSON and exits if the user proceeds;
        if canceled, returns to LaunchScreen.
        """
        from .screens.home import HomeScreen
        home_screen = HomeScreen(default_path=path)
        settings_json = await self.ui.push_screen_wait(home_screen)
        if not settings_json:
            return "launch", ()
        return None, (settings_json,)
