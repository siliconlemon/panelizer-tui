from textual import events
from textual.app import ComposeResult
from textual.events import Click
from textual.keys import Keys
from textual.message import Message
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Switch, Label


class Toggle(Widget, inherit_css=False):
    """A button emulation combining a Switch and a clickable label within a horizontal container."""

    class Changed(Message):
        """Posted when the switch's active state changes."""

        def __init__(self, ref: "Toggle", active: bool) -> None:
            super().__init__()
            self.ref = ref
            self.active = active

    is_active: reactive[bool] = reactive(False)

    DEFAULT_CSS = """
        Toggle {
            width: 100%;
            height: 3;
            padding: 0 1 0 0;
            layout: horizontal;
            text-align: center;
            border: round $accent 50%;
            
            &.--hover, &:focus-within {
                border: round $accent;
                &.-toggled {
                    border: round $success;
                }
                Switch {
                    &.-on .switch--slider {
                        color: $success-lighten-1;
                    }
                    & .switch--slider {
                        color: $accent 70%;
                    }
                }
            }

            &:focus-within.--hover {
                border: round $accent 60%;
                &.-toggled {
                    border: round $success 60%;
                }
                Label {
                    color: $text 60%;
                }
                &.-toggled Label {
                    color: $success-lighten-1 60%;
                }
                Switch {
                    &.-on .switch--slider {
                        color: $success-lighten-1 60%;
                    }
                    & .switch--slider {
                        color: $accent 50%;
                    }
                }
            }

            &.-toggled Label {
                color: $success-lighten-1;
            }

            Label {
                width: 1fr;
                min-height: 1;
                text-align: center;
                padding: 0 1 0 1;
                text-style: bold;
                background: transparent;
                color: $text;
            }

            &:focus-within Label {
                text-style: $button-focus-text-style;
            }

            Switch {
                height: 1;
                padding: 0;
                margin: 0 2 0 1;
                background: transparent;
                border: none;

                &.-on .switch--slider {
                    color: $success;
                    border: none;
                }

                & .switch--slider {
                    color: $accent 40%;
                    background: $panel-darken-3;
                    border: none;
                }

                &:focus {
                    border: none;
                    background: $accent;
                    color: $accent;
                }
            }
        }
    """

    def __init__(
            self,
            *,
            switch_id: str | None = None,
            text: str,
            is_active: bool = False,
            **kwargs
    ):
        super().__init__(**kwargs)
        self.is_active = is_active

        self.switch = Switch(value=is_active, animate=False, id=switch_id if switch_id else self.id)
        self.text = Label(" " + text + " ")

    def compose(self) -> ComposeResult:
        yield self.switch
        yield self.text

    def on_switch_changed(self, event: Switch.Changed) -> None:
        event.stop()
        self.is_active = event.value
        local_is_active = event.value
        self.post_message(self.Changed(self, local_is_active))

    def on_click(self, event: Click) -> None:
        if event.widget is self.text or event.widget is self:
            event.stop()
            self.switch.toggle()
        elif event.widget is self.switch:
            event.stop()
        self.switch.focus()
        if self.switch.value:
            self.add_class("-toggled")
        else:
            self.remove_class("-toggled")

    def _on_key(self, event: events.Key) -> None:
        if event.key == Keys.Enter or event.key == Keys.Space:
            if not self.switch.value:
                self.add_class("-toggled")
            else:
                self.remove_class("-toggled")

    def on_enter(self) -> None:
        self.add_class("--hover")

    def on_leave(self) -> None:
        self.remove_class("--hover")