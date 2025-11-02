from typing import ClassVar

from textual.widgets import Input


class NeonInput(Input, inherit_css=False):
    """A skin for textual's native Input widget."""
    DEFAULT_CSS = """
    NeonInput {
        color: $text;
        border: round $foreground 70%;
        background: transparent;
        scrollbar-size-horizontal: 0;
        width: 100%;
        height: 3;
        min-width: 10;
        min-height: 1;
        padding: 0 1;
        margin: 0;
        
        /* Does not allow compact layout */
        &.-textual-compact {
            border: round $foreground 70%;
            height: 3;
            padding: 0 1;
            &.-invalid {
                border: round $error 60%;
            }
        }
        &:focus, &:hover {
            color: $text;
            background: transparent;
            border: round $accent;
        }
        &:focus:hover {
            color: $text 70%;
            border: round $accent 60%;
        }
        &:ansi {
            background: ansi_default;
            color: ansi_default;
            & > .input--cursor {
                text-style: reverse;
            }
            & > .input--placeholder, & > .input--suggestion {
                text-style: dim;
                color: ansi_default;
            }
            &.-invalid {
                border: tall ansi_red;
            }
            &.-invalid:focus {
                border: tall ansi_red;
            }
        }
        &.-invalid {
            border: round $error 60%;
        }
        &.-invalid:focus {
            border: round $error;
        }
        
        & > .input--cursor {
            background: $input-cursor-background;
            color: $input-cursor-foreground;
            text-style: $input-cursor-text-style;
        }
        & > .input--selection {
            background: $input-selection-background;
        }
        & > .input--placeholder, & > .input--suggestion {
            color: $text-disabled;
        } 
    }
    """
    COMPONENT_CLASSES: ClassVar[set[str]] = {
        "input--cursor",
        "input--placeholder",
        "input--suggestion",
        "input--selection",
    }