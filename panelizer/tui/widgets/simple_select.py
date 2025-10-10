from textual.app import ComposeResult
from textual.containers import Container
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Static, Select


class SimpleSelect(Widget):
    """A widget for selecting the background color."""
    DEFAULT_CSS = """
        SimpleSelect {
            height: 4;
            margin-right: 1;
            border: none;

            .simple-select-input {
                min-height: 3;
                width: 1fr;
            }

            SelectCurrent {
                color: $text;
                border: none;
            }

            OptionList {
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
        yield Static(self.label, classes="input-label", id="label")
        with Container(id="simple-select-container"):
            yield Select(
                id=self.select_id if self.select_id else None,
                classes="simple-select-input",
                compact=True,
                value=self.initial_value,
                allow_blank=False,
                options=self.options,
            )

    def on_enter(self) -> None:
        self.add_class("--hover")

    def on_leave(self) -> None:
        self.remove_class("--hover")