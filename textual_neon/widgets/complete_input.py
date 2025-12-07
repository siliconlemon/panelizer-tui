from typing import Optional, Literal

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widget import Widget

from textual_neon.widgets.neon_input import NeonInput
from textual_neon.widgets.inert_label import InertLabel


class CompleteInput(Widget):
    """
    A labeled input widget with an optional unit label to the right. Uses NeonInput.

    NOTE: If you're using a single CompleteInput in your layout and stuff starts disappearing,
    wrap this in a Container or a Horizontal. This is a `textual` issue with the Input widget that I couldn't fix.
    """
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

    def __init__(
        self,
        *,
        label: Optional[str] = None,
        value: int = 0,
        unit: Optional[str] = None,
        type_: Literal["integer", "number", "text"] = "integer",
        **kwargs,
    ):
        input_id = None
        if "id" in kwargs and kwargs["id"]:
            input_id = kwargs["id"]
            kwargs["id"] = f"comp-input-{kwargs['id']}"
        else:
            kwargs["id"] = "input"
        super().__init__(**kwargs)
        self.input_id = input_id or "input"
        self.label = label
        self.value = value
        self.unit = unit
        self.type_ = type_

    def compose(self) -> ComposeResult:
        with Vertical():
            if self.label:
                yield InertLabel(self.label, id="label")
            with Horizontal():
                yield NeonInput(str(self.value), id=self.input_id, type=self.type_, classes="single-input")
                if self.unit:
                    yield InertLabel(self.unit, id="unit", disabled=True)
