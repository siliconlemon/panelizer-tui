from textual.app import ComposeResult
from textual.containers import Container
from textual.reactive import reactive
from textual.widget import Widget

from textual_neon.widgets.neon_select import NeonSelect
from textual_neon.widgets.inert_label import InertLabel


class CompleteSelect(Widget):
    """A bundle of an InertLabel, a Container and a NeonSelect to make selector insertions easier."""
    DEFAULT_CSS = """
    CompleteSelect {
        height: 4;
        border: none;
        
        NeonSelect OptionList {
            margin-right: 3;
        }
    }
    """

    def __init__(
            self,
            *,
            select_id: str,
            label: str,
            initial: str,
            options: list[tuple[str, str]],
            **kwargs
    ):
        if select_id:
            self.select_id = select_id
        super().__init__(**kwargs)
        self.label = label
        self.initial_value = initial
        self.options = [(f" {label.strip()} ", value) for label, value in options]

    label_hovered = reactive(False)

    def compose(self) -> ComposeResult:
        yield InertLabel(self.label, classes="input-label", id="label")
        with Container():
            yield NeonSelect(
                id=self.select_id if self.select_id else None,
                classes="neon-select",
                value=self.initial_value,
                allow_blank=False,
                options=self.options,
            )

    def on_enter(self) -> None:
        self.add_class("--hover")

    def on_leave(self) -> None:
        self.remove_class("--hover")