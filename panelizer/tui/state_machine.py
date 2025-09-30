from pathlib import Path
from typing import TYPE_CHECKING, Callable, Awaitable

if TYPE_CHECKING:
    from . import PanelizerTUI

class StateMachine:
    """
    Manages the screen and workflow state transitions for the PanelizerTUI application.
    Each state is implemented as a coroutine and referenced by a string key.
    Extends the PanelizerTUI functionality with a parent reference.
    """

    def __init__(self, *, ui: "PanelizerTUI"):
        self.ui = ui
        self.states: dict[str, Callable[..., Awaitable[tuple[str | None, tuple]]]] = {
            "launch": self.launch_screen_state,
        }

    async def run(self) -> None:
        """
        Runs the state machine loop.
        Looks up and calls each state coroutine by its string key until a terminal state is reached.
        """
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
        Presents the LaunchScreen and determines the next state.
        Exits after completion, returning the selected path or None.
        """
        path = await self.ui.push_screen_wait("launch")
        if isinstance(path, Path) and path.exists():
            return None, (path,)
        return None, (path,)