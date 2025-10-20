import inspect
from collections.abc import Callable
from typing_extensions import override

from textual.message import Message

from textual_neon.widgets.neon_button import NeonButton


class ChoiceButton(NeonButton, inherit_css=True):
    """
    A dynamic button widget for selecting one of multiple options with added functionality on-press.
    Based on NeonButton.
    """
    DEFAULT_CSS = """
    ChoiceButton {
        width: 1fr;
        height: auto;
        min-height: 3;
        min-width: 14;
        padding: 0;
        color: $accent 60%;
        border: round $accent 50%;
        
        &:hover {
            color: $text;
            border: round $accent;
        }
        &:focus {
            color: $text;
            border: round $accent 60%;
            &:hover {
                color: $text;
                border: round $accent;
            }
        }
        &.--selected {
            color: $text;
            border: round $accent;
            &:hover {
                color: $text;
                border: round $accent;
            }
            &:focus {
                color: $text;
                border: round $accent;
                &:hover {
                    color: $text;
                    border: round $accent 60%;
                }
            }
        }
    }
    """

    class Selected(Message):
        """Posted when this ChoiceButton is selected (pressed)."""
        def __init__(self, sender: "ChoiceButton") -> None:
            super().__init__()
            self.button = sender

    def __init__(
        self,
        *,
        label: str,
        action: Callable | None,
        label_when_selected: str | Callable[[], str] | None = None,
        **kwargs,
    ) -> None:
        super().__init__(label=label, **kwargs)
        self._label_default = label
        self.action = action
        self.label_when_selected = label_when_selected
        self._selected = False

    @property
    def selected(self) -> bool:
        return self._selected

    @staticmethod
    def decorate_selected_text(text: str) -> str:
        return f"\\[ {text.strip()} ]"

    @staticmethod
    def decorate_unselected_text(text: str) -> str:
        return f" {text.strip()} "

    def set_selected(self, value: bool) -> None:
        self._selected = value
        self.set_class(value, "--selected")
        if value:
            if self.label_when_selected:
                new_label = self.label_when_selected() \
                    if callable(self.label_when_selected) else self.label_when_selected
            else:
                new_label = self._label_default
            new_label = new_label.strip()
            self.label = self.decorate_selected_text(new_label)
        else:
            self.label = self.decorate_unselected_text(self._label_default)

    async def on_button_pressed(self, event) -> None:
        await self.select()
        self.post_message(self.Selected(self))
        event.stop()

    async def select(self):
        if self.action is not None:
            if inspect.iscoroutinefunction(self.action):
                await self.action()
            else:
                result = self.action()
                if inspect.isawaitable(result):
                    await result

    @override
    def watch_label(self, new_label: str) -> None:
        """
        Overrides the parent NeonButton.watch_label to prevent re-formatting.
        ChoiceButton's label formatting is managed entirely by the
        set_selected() method.
        """
        pass
