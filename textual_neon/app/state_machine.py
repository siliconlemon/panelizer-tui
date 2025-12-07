from typing import Any, Callable, TYPE_CHECKING, Type

from textual.screen import Screen

from textual_neon.utils.screen_data import ScreenData

if TYPE_CHECKING:
    from textual_neon.app.neon_app import NeonApp


class StateMachine:
    """
    Handles UI workflow and screen transitions for the NeonApp.
    States are registered by the descendants of NeonApp, allowing data-driven configuration
    of screens, validation, and flow, detached from the base class.

    Note: In some use cases, it might be better to only register the launch and home screens with the app
    and handle multiple screen pushes from the home screen (or whatever you might call it, it's user-defined).
    """
    class StateSpec:
        def __init__(
            self,
            screen_class: Type[Screen],
            kwargs: dict | None = None,
            next_state: str | None = None,
            fallback: str | None = None,
            validate: Callable[[Any], bool] | None = None,
            data_from_result: Callable[[Any], ScreenData] | None = None,
        ):
            self.screen = screen_class
            self.kwargs = kwargs or {}
            self.next = next_state
            self.fallback = fallback
            self.validate = validate or (lambda result: True)
            self.data_from_result = data_from_result or (lambda result: None)

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
        screen_class: Type[Screen],
        kwargs: dict | None = None,
        next_state: str | None = None,
        fallback: str | None = None,
        validate: Callable[[Any], bool] | None = None,
        data_from_result: Callable[[Any], ScreenData] | None = None,
    ) -> None:
        # noinspection GrazieInspection
        """
        Registers a new state for the state machine.

        This links a state name (e.g., "home") to a Screen class and defines
        the rules for transitioning to the *next* state based on the current
        screen's `dismiss()` result.

        Args:
            state_name: A unique string name for this state (e.g., "launch", "home").

            screen_class: The `Screen` class to display for this state (e.g., `HomeScreen`).

            kwargs: (Optional) A dict of static, named arguments to pass to the
                screen's `__init__` (e.g., titles, labels, or static configuration).

            next_state: The `state_name` to transition to if validation passes.
                Can be a string or a `lambda result: ...` for dynamic transitions.

            fallback: (Optional) The `state_name` to transition to if validation fails.
                If `None`, the app will exit on validation failure.

            validate: (Optional) A `lambda result: ...` that receives the data from
                `screen.dismiss(result)`. Must return `True` to proceed to `next_state`
                or `False` to go to `fallback`. Defaults to always `True`.

            data_from_result: (Optional) A `lambda result: ...` that receives the
                `dismiss` result and must return a `ScreenData` object. This object
                will be passed as the *first positional argument* to the *next*
                screen's `__init__`.

        Usage:
        ::
            # In your NeonApp descendant's __init__:
            self.state_machine.register(
                "done",
                screen_class=DoneScreen,
                kwargs={
                    "text": "Good job! You're done.",
                },
                next_state="home",
                validate=lambda result: result == "home",
                data_from_result=lambda result: ScreenData(source="done", payload=None)
            )
        """
        self.specs[state_name] = StateMachine.StateSpec(
            screen_class=screen_class,
            kwargs=kwargs,
            next_state=next_state,
            fallback=fallback,
            validate=validate,
            data_from_result=data_from_result,
        )
        self._registered = True

    async def run(self, start_state: str = "launch") -> None:
        """Runs the state machine loop from the initial state until exit."""
        state_name = start_state
        data: ScreenData | None = None
        last_result: Any = None

        try:
            while state_name:
                spec = self.specs.get(state_name)
                if not spec:
                    self._app.exit(f"[StateMachine Error]: No spec for state '{state_name}'.")
                    return

                scr_class = spec.screen
                scr_kwargs = spec.kwargs

                if data is None:
                    screen_instance = scr_class(**scr_kwargs)
                else:
                    screen_instance = scr_class(data, **scr_kwargs)

                result = await self._app.push_screen_wait(screen_instance)
                last_result = result

                if spec.validate(result):
                    if callable(spec.next):
                        next_state = spec.next(result)
                    else:
                        next_state = spec.next
                    next_data = spec.data_from_result(result)

                elif spec.fallback:
                    next_state = spec.fallback
                    next_data = None
                else:
                    next_state = None
                    next_data = None

                state_name = next_state
                data = next_data
            self._app.exit(last_result)

        except Exception as e:
            self._app.exit(f"[Exception]: {e}")