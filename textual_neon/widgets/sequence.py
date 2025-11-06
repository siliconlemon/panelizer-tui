import asyncio
import inspect
from typing import NamedTuple,Literal, Callable, Any, TypeAlias, cast

from textual import on
from textual.containers import Horizontal, Vertical
from textual.message import Message
from textual.widget import Widget

from textual_neon.widgets.neon_button import NeonButton


SequenceTask: TypeAlias = Callable[[], Any]
SequenceValidator: TypeAlias = Callable[[Any], bool]

class _StepState(NamedTuple):
    """Internal dataclass to store the state of each step."""
    button: NeonButton
    task: SequenceTask
    validator: SequenceValidator
    result: Any | None = None
    is_valid: bool | None = None


class Sequence(Widget, inherit_css=True):
    """
    A widget that manages a sequence of steps, each represented by a NeonButton.
    It ensures steps are executed in order and handles success, failure, and
    rolling back to previous steps.

    Usage:
    ::
        # Inside your Screen (a widget would call self.screen.notify)
        ...
        def compose(self) -> ComposeResult:
            yield self._build_my_sequence()
        ...
        def _build_my_sequence(self) -> Sequence:
            seq = Sequence(name="Processing Steps", id="my-sequence")
            seq.register_step(
                label="Step 1: Validate Data",
                task=self._run_validation_task,
                validator=self._check_task_result
            )
            seq.register_step(
                label="Step 2: Run Process",
                task=self._run_main_task,
                validator=self._check_task_result
            )
            return seq
        ...
        async def _task_pass(self) -> str:
            self.notify("Running step (will pass)...", title="Sequence Task")
            await asyncio.sleep(0.75)
            return "Task Succeeded"
        ...
        async def _task_fail(self) -> str:
            self.notify("Running step (will fail)...", title="Sequence Task")
            await asyncio.sleep(0.75)
            return "Task Reported Failure"
        ...
        @staticmethod
        def _demo_validator(result) -> bool:
            if isinstance(result, str):
                return result == "Task Succeeded"
            return False
        ...
        @on(Sequence.StateChange, "#my-sequence")
        def sequence_state_changed(self, event: Sequence.StateChange) -> None:
            if event.success:
                self.notify(f"Step {event.step_index + 1} Succeeded!")
            else:
                self.notify(f"Step {event.step_index + 1} Failed!", severity="error")
        ...
        # Reset the sequence if a relevant setting changes
        @on(Input.Changed, "#some-input")
        def input_changed(self) -> None:
            self.query_one("#my-sequence", Sequence).current_step = 0
    """
    DEFAULT_CSS = """
    Sequence {
        height: auto;
        width: 100%;
        
        Horizontal, Vertical {
            border: round $foreground 60%;
            border-title-color: $foreground 70%;
            height: auto;
        }
        & NeonButton {
            width: 1fr;
        }
    }
    """

    class StateChange(Message):
        """
        Posted *after* a step's task and validator have run.
        This signals the outcome of the step.
        """
        def __init__(
                self,
                sender: "Sequence",
                step_index: int,
                success: bool,
                task_result: Any,
        ) -> None:
            super().__init__()
            self._sender_widget = sender
            self.step_index = step_index
            self.success = success
            self.task_result = task_result

        @property
        def control(self) -> "Sequence":
            """The Sequence widget that sent the message."""
            return self._sender_widget

        @property
        def sequence(self) -> "Sequence":
            """A convenient alias for self.control."""
            return self.control


    def __init__(
            self,
            *,
            name: str,
            orientation: Literal["horizontal", "vertical"] = "horizontal",
            **kwargs,
    ) -> None:
        """
        Initializes the Sequence widget.

        Args:
            name: The name to display in the border title.
            orientation: The layout orientation ("horizontal" or "vertical").
            **kwargs: Additional keyword arguments for the Widget.
        """
        super().__init__(name=name, **kwargs)
        self.orientation = orientation
        self.border_title = name
        self._steps: list[_StepState] = []
        self._buttons: list[NeonButton] = []
        self._container: Horizontal | Vertical | None = None

        self._current_step_index = 0
        """The index of the step that is currently active (primary)."""

        self._processing_step_index: int | None = None
        """The index of the step currently being executed by a worker, or None."""

    def register_step(
            self,
            label: str,
            task: SequenceTask,
            validator: SequenceValidator,
    ) -> None:
        """
        Registers a new step in the sequence.

        This method should be called *before* the widget is mounted
        (e.g., in the parent's `compose` method).

        Args:
            label: The text label for the step's button.
            task: A callable (sync or async) to execute when the button is pressed.
            validator: A sync callable that takes the task's result and returns
                       True for success or False for failure.
        """
        btn = NeonButton(label=label)
        if not self._steps:
            btn.variant = "primary"
            btn.disabled = False
        else:
            btn.disabled = True

        self._buttons.append(btn)
        self._steps.append(
            _StepState(button=btn, task=task, validator=validator)
        )

    def compose(self):
        """Composes the widget's layout and buttons."""
        container_cls = (
            Horizontal if self.orientation == "horizontal" else Vertical
        )
        num_buttons = len(self._buttons)

        with container_cls() as container:
            for idx, btn in enumerate(self._buttons):
                is_last = idx == num_buttons - 1
                # noinspection DuplicatedCode
                if self.orientation == "horizontal":
                    right = 1 if is_last else 2
                    left = 2 if is_last else 1
                    btn.styles.margin = (0, right, 0, left)
                else:
                    btn.styles.margin = (0, 1, 0, 1)
                yield btn
        self._container = container

    async def on_mount(self) -> None:
        """
        Sets the border title and validates that steps have been registered.

        Raises:
            ValueError: If no steps were registered, using `register_step`
                before the widget is mounted.
        """
        if not self._steps:
            raise ValueError(
                "Sequence widget mounted without any steps. "
                "Call `register_step` in the parent's `compose` method."
            )
        if self._container:
            self._container.border_title = self.border_title

    def set_step(self, target_index: int) -> None:
        """
        Sets the current active step, rolling back if necessary.
        Does not execute any button logic, only moves focused based on external needs, like a change of settings.
        Resets the result and status of all the steps left behind when rolling back.

        Args:
            target_index: The index of the step to make active.
        """
        if not (0 <= target_index < len(self._steps)):
            self.app.log.warning(
                f"Attempted to set invalid sequence step: {target_index}"
            )
            return
        current_index = self._current_step_index
        if target_index > current_index:
            self.screen.notify(
                "Cannot programmatically advance the sequence.",
                severity="error",
                title="Invalid Step"
            )
        elif target_index < current_index:
            self._reset_to(target_index)

    @on(NeonButton.Pressed)
    async def _handle_press(self, event: NeonButton.Pressed) -> None:
        """Handles all button presses within the sequence."""
        event.stop()
        pressed_button = cast(NeonButton, event.button)

        try:
            pressed_index = self._buttons.index(pressed_button)
        except ValueError:
            return

        if self._processing_step_index is not None:
            self.screen.notify("A step is already in progress.", severity="warning")
            return

        is_completed = (
                pressed_index < self._current_step_index
                and not self._steps[pressed_index].button.disabled
        )
        if is_completed:
            self._reset_to(pressed_index)

        if pressed_index == self._current_step_index:
            self._processing_step_index = pressed_index
            step = self._steps[pressed_index]

            self.run_worker(
                self._execute_step(step.task, step.validator, pressed_index),
                exclusive=True,
                group=f"sequence_step_{self.id}",
            )

    async def _execute_step(
            self, task: SequenceTask, validator: SequenceValidator, step_index: int
    ) -> None:
        """A worker function to execute a task and its validator. Posts a StateChange message with the result."""
        try:
            task_result: Any
            if inspect.iscoroutinefunction(task):
                task_result = await task()
            else:
                task_result = await asyncio.to_thread(task)

            try:
                is_valid = validator(task_result)
            except Exception as e:
                self.app.log.error(f"Sequence validator for step {step_index} failed: {e}")
                is_valid = False
                task_result = e

        except Exception as e:
            self.app.log.error(f"Sequence task for step {step_index} failed: {e}")
            is_valid = False
            task_result = e

        self.post_message(
            self.StateChange(self, step_index, is_valid, task_result)
        )

    @on(StateChange)
    def _handle_state_change(self, event: StateChange) -> None:
        """Listens for our own message to update the UI state."""
        if event.control is not self:
            return
        event.stop()
        step_index = event.step_index
        if self._processing_step_index != step_index:
            return
        step = self._steps[step_index]
        self._steps[step_index] = step._replace(
            result=event.task_result, is_valid=event.success
        )

        if event.success:
            step.button.variant = "default"
            next_step_index = step_index + 1
            if next_step_index < len(self._steps):
                self._current_step_index = next_step_index
                next_step = self._steps[next_step_index]
                next_step.button.disabled = False
                next_step.button.variant = "primary"
            else:
                self._current_step_index = len(self._steps)
                self.notify("Sequence complete!", severity="information")
        else:
            step.button.variant = "error"
        self._processing_step_index = None

    def _reset_to(self, target_index: int) -> None:
        """Resets the sequence state back to the target_index, clearing all later step states."""
        self._current_step_index = target_index
        target_step = self._steps[target_index]
        target_step.button.variant = "primary"
        self._steps[target_index] = target_step._replace(
            result=None, is_valid=None
        )
        for i in range(target_index + 1, len(self._steps)):
            step = self._steps[i]
            step.button.variant = "default"
            step.button.disabled = True
            self._steps[i] = step._replace(result=None, is_valid=None)

    def get_step_result(self, index: int) -> Any | None:
        """Returns the cached result for a given step or None."""
        if 0 <= index < len(self._steps):
            return self._steps[index].result
        return None

    def get_step_status(self, index: int) -> bool | None:
        """Returns the cached validation status (True/False) for a step or None."""
        if 0 <= index < len(self._steps):
            return self._steps[index].is_valid
        return None

    @property
    def all_results(self) -> list[Any | None]:
        """Returns a list of all cached results."""
        return [step.result for step in self._steps]

    @property
    def all_statuses(self) -> list[bool | None]:
        """Returns a list of all cached validation statuses."""
        return [step.is_valid for step in self._steps]

    @property
    def current_step(self) -> int:
        """Returns the index of the current active (primary) step."""
        return self._current_step_index

    @current_step.setter
    def current_step(self, target_index: int) -> None:
        """Sets the current active step, does not execute any button logic or go over the last available step."""
        self.set_step(target_index)
