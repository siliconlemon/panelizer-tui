from typing import Optional, Literal

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widget import Widget
from textual.widgets import Input

from textual_neon.widgets.inert_label import InertLabel


class CompleteInput(Widget):
    """A labeled input widget with an optional unit label to the right."""
    DEFAULT_CSS = """
    CompleteInput {
        width: 100%;
        height: auto;
        layout: grid;
        
        InertLabel#label {
            margin-left: 1;
        }
        
        InertLabel#unit {
            color: $text-muted;
            width: 2;
            margin: 1 0 0 1;
        }
        
        Input {
            color: $text;
            border: round $accent 50%;
            background: transparent;
            color: $text;
            width: 1fr;
            min-width: 10;
            min-height: 1;
            padding: 0 1;
            margin: 0;
            
            &:focus, &:hover {
                color: $text;
                border: round $accent;
                background: transparent;
            }
        }
    }
    """

    def __init__(
        self,
        *,
        input_id: Optional[str] = None,
        label: Optional[str] = None,
        value: int = 0,
        unit: Optional[str] = None,
        type_: Literal["integer", "number", "text"] = "integer",
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.label = label
        self.value = value
        self.input_id = input_id
        self.unit = unit
        self.type_ = type_

    def compose(self) -> ComposeResult:
        with Vertical():
            if self.label:
                yield InertLabel(self.label, id="label")
            with Horizontal():
                yield Input(str(self.value), id=self.input_id, type=self.type_, classes="single-input")
                if self.unit:
                    yield InertLabel(self.unit, id="unit", disabled=True)
