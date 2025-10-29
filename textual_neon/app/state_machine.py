from typing import Any, Callable, TYPE_CHECKING

if TYPE_CHECKING:
    from .neon_app import NeonApp


class StateMachine:
    """
    Handles UI workflow and screen transitions for the PanelizerTUI app.
    States are registered by PanelizerTUI, allowing data-driven configuration
    of screens, validation, and flow, detached from the base class.
    """
    class StateSpec:
        def __init__(
            self,
            screen: Any,
            next_state: str | None = None,
            fallback: str | None = None,
            validate: Callable[[Any], bool] | None = None,
            args_from_result: Callable[[Any], tuple] = None,
        ):
            self.screen = screen
            self.next = next_state
            self.fallback = fallback
            self.validate = validate or (lambda result: True)
            self.args_from_result = args_from_result or (lambda result: ())

    def __init__(self, *, app: "NeonApp"):
        """Initializes the state machine with UI reference."""
        self._app: NeonApp = app
        self._registered: bool = False
        self.specs: dict[str, StateMachine.StateSpec] = {}

    @property
    def registered(self) -> bool:
        """Returns True if any states are registered."""
        return self._registered

    def register(
        self,
        state_name: str,
        *,
        screen: Any,
        next_state: str | None = None,
        fallback: str | None = None,
        validate: Callable[[Any], bool] | None = None,
        args_from_result: Callable[[Any], tuple] | None = None,
    ) -> None:
        """
        Registers a new state for the state machine, including its screen,
        transition logic, and result validation.
        """
        self.specs[state_name] = StateMachine.StateSpec(
            screen=screen,
            next_state=next_state,
            fallback=fallback,
            validate=validate,
            args_from_result=args_from_result,
        )
        self._registered = True

    async def run(self, start_state: str = "launch") -> None:
        """Runs the state machine loop from the initial state until exit."""
        state_name = start_state
        args = ()

        try:
            while state_name:
                spec = self.specs.get(state_name)
                if not spec:
                    self._app.exit("No spec in the StateMachine loop.")
                    return
                scr = (
                    spec.screen
                    if not isinstance(spec.screen, str)
                    else self._app.SCREENS[spec.screen]
                )
                if callable(scr):
                    screen_instance = scr(*args) if args else scr()
                else:
                    screen_instance = scr
                result = await self._app.push_screen_wait(
                    screen_instance if not isinstance(spec.screen, str) else spec.screen
                )
                if spec.validate(result):
                    next_state = spec.next
                    next_args = spec.args_from_result(result)
                elif spec.fallback:
                    next_state = spec.fallback
                    next_args = ()
                else:
                    next_state = None
                    next_args = ()
                state_name = next_state
                args = next_args

            self._app.exit(args[0] if args else None)

        except Exception as e:
            self._app.exit(e)
