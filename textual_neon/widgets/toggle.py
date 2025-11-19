from textual import events
from textual.app import ComposeResult
from textual.events import Click
from textual.keys import Keys
from textual.message import Message
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Switch

from ..widgets.inert_label import InertLabel

class Toggle(Widget, inherit_css=False, can_focus=False):
    """A button emulation combining a Switch and a clickable label within a horizontal container."""
    DEFAULT_CSS = """
    Toggle {
        width: 100%;
        height: 3;
        padding: 0 1 0 0;
        layout: horizontal;
        border: round $foreground 70%;
        text-style: none;
        
        &:focus {
            text-style: $button-focus-text-style;
        }
        &:hover {
            color: $foreground 60%;
            border: round $accent;
        }
        &:focus:hover {
            color: $foreground 60%;
            border: round $accent 60%;
        }
        &.-active {
            color: $foreground 40%;
            border: round $accent 40%;
        }
        &:disabled {
            color: $foreground 40%;
            border: round $accent 40%;
        }
        &:focus-within InertLabel {
            text-style: $button-focus-text-style;
        }
        &.-on InertLabel {
            color: $success-lighten-2;
        }
        
        Switch {
            height: 1;
            padding: 0;
            margin: 0 1 0 1;
            background: transparent;
            border: none;
            
            /*TODO: The values for success and foreground do not match */
            
            &.-on .switch--slider {
                color: $success-lighten-2;
                background: $panel-darken-3;
                border: none;
            }
            & .switch--slider {
                color: $foreground 50%;
                background: $panel-darken-3;
                border: none;
            }
            &:focus {
                color: $text-accent;
                background: $panel-darken-3;
                border: none;
            }
        }
        
        InertLabel {
            width: 1fr;
            min-height: 1;
            text-align: left;
            padding: 0 1 0 1;
            text-style: bold;
            background: transparent;
            color: $foreground 90%;
        }
        
        &.--hover {
            border: round $accent;
            Switch {
                &.-on .switch--slider {
                    color: $success-lighten-2;
                    background: $panel-darken-3;
                }
                & .switch--slider {
                    color: $foreground 80%;
                    background: $panel-darken-3;
                }
            }
        }

        &:focus-within {
            border: round $accent;
            Switch {
                &.-on .switch--slider {
                    color: $success-lighten-2;
                    background: $panel-darken-3;
                }
                & .switch--slider {
                    color: $foreground 80%;
                    background: $panel-darken-3;
                }
            }
        }

        &:focus-within.--hover {
            border: round $accent 60%;
            InertLabel {
                color: $foreground 60%;
            }
            &.-on InertLabel {
                color: $success-lighten-2 60%;
            }
            Switch {
                &.-on .switch--slider {
                    color: $success-lighten-2 80%;
                    background: $panel-darken-3;
                }
                & .switch--slider {
                    color: $foreground 60%;
                    background: $panel-darken-3;
                }
            }
        }
    }
    """

    class Changed(Message):
        """Posted when the switch's active state changes."""
        def __init__(self, ref: "Toggle", active: bool) -> None:
            super().__init__()
            self.ref = ref
            self.active = active

        @property
        def control(self) -> "Toggle":
            """The Toggle widget that sent the message."""
            return self.ref

    def __init__(
            self,
            *,
            switch_id: str | None = None,
            text: str,
            is_active: bool = False,
            **kwargs
    ):
        super().__init__(**kwargs)
        self._switch = Switch(value=is_active, animate=False, id=switch_id if switch_id else self.id)
        self._label = InertLabel(" " + text + " ", )
        self.set_class(is_active, "-on")

    @property
    def is_active(self) -> bool:
        """The active state of the toggle, sourced from the internal Switch."""
        return self._switch.value

    @is_active.setter
    def is_active(self, new_value: bool) -> None:
        """
        Sets the active state of the toggle.
        This will command the internal Switch to change.
        """
        self._switch.value = new_value

    def compose(self) -> ComposeResult:
        yield self._switch
        yield self._label

    def on_switch_changed(self, event: Switch.Changed) -> None:
        """When the switch changes, update our CSS and notify parent."""
        event.stop()
        self.set_class(event.value, "-on")
        self.post_message(self.Changed(self, event.value))

    def on_click(self, event: Click) -> None:
        if event.widget is self._label or event.widget is self:
            event.stop()
            self._switch.toggle()
        elif event.widget is self._switch:
            event.stop()
        self._switch.focus()

    def _on_key(self, event: events.Key) -> None:
        if event.key == Keys.Enter or event.key == Keys.Space:
            event.stop()
            self._switch.toggle()

    def on_enter(self) -> None:
        self.add_class("--hover")

    def on_leave(self) -> None:
        self.remove_class("--hover")