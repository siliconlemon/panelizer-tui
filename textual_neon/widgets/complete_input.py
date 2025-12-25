from typing import Optional, Literal, List

from textual import on
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.css.query import NoMatches
from textual.message import Message
from textual.validation import Validator
from textual.widget import Widget
from textual.widgets import Input

from textual_neon.widgets.neon_input import NeonInput
from textual_neon.widgets.inert_label import InertLabel


class CompleteInput(Widget):
    DEFAULT_CSS = """
    CompleteInput {
        width: 100%;
        height: auto;
        layout: grid;

        InertLabel#label {
            margin-left: 1;
        }

        NeonInput {
            width: 1fr;
        }

        InertLabel#unit {
            color: $foreground 70%;
            width: 2;
            margin: 1 0 0 1;
        }
    }
    """

    class Blurred(Message):
        def __init__(self, sender: "CompleteInput", value: str) -> None:
            super().__init__()
            self.input = sender
            self.value = value

        @property
        def control(self) -> "CompleteInput":
            return self.input

    class Submitted(Message):
        def __init__(self, sender: "CompleteInput", value: str) -> None:
            super().__init__()
            self.input = sender
            self.value = value

        @property
        def control(self) -> "CompleteInput":
            return self.input

    def __init__(
            self,
            *,
            label: Optional[str] = None,
            value: int = 0,
            unit: Optional[str] = None,
            type_: Literal["integer", "number", "text"] = "integer",
            validators: List[Validator] = None,
            **kwargs,
    ):
        super().__init__(**kwargs)
        self.label = label
        self._initial_value = value
        self.unit = unit
        self.type_ = type_
        self._initial_validators = validators or []

    def compose(self) -> ComposeResult:
        with Vertical():
            if self.label:
                yield InertLabel(self.label, id="label")
            with Horizontal():
                yield NeonInput(
                    str(self._initial_value),
                    id="inner-input",
                    type=self.type_,
                    validators=self._initial_validators,
                    classes="single-input"
                )
                if self.unit:
                    yield InertLabel(self.unit, id="unit", disabled=True)

    @property
    def value(self) -> str:
        """Proxy value from inner input."""
        try:
            return self.query_one("#inner-input", NeonInput).value
        except NoMatches:
            return str(self._initial_value)

    @value.setter
    def value(self, new_value: str) -> None:
        self.query_one("#inner-input", NeonInput).value = str(new_value)

    @property
    def validators(self) -> List[Validator]:
        """
        Proxy the `validators` list from the inner input.
        This allows 'widget.validators.append()' to work from the outside.
        """
        try:
            return self.query_one("#inner-input", NeonInput).validators
        except NoMatches:
            return self._initial_validators

    @on(NeonInput.Blurred)
    def _catch_blur(self, event: Input.Blurred) -> None:
        event.stop()
        self.post_message(self.Blurred(self, self.value))

    @on(Input.Submitted)
    def _catch_submitted(self, event: Input.Submitted) -> None:
        event.stop()
        self.post_message(self.Submitted(self, self.value))