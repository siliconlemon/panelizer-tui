from textual.widgets import Select

# TODO: Implement all of the css and classes, drop the inheritance
class NeonSelect(Select, inherit_css=True):
    """A skin for textual's native Select widget."""
    DEFAULT_CSS = """
    NeonSelect {
        min-height: 3;
        width: 1fr;
        border: none !important;
        
        SelectCurrent {
            color: $text;
            border: none !important;
            background: transparent;
            margin: 0;
            padding: 0 0 0 0 !important;
            height: 3;
        }
        
        & > SelectOverlay {
            padding: 0 0 0 1 !important;
        }
        
        OptionList {
            background: transparent;
            padding: 0;
            &:focus-within, &:hover {
                border: round $accent 50%;
            }
        }
        
        SelectCurrent > #label {
            color: $text;
            border: round $accent 50%;
            background: transparent;
            &:hover {
                border: round $accent;
            }
        }
        
        &:focus SelectCurrent #label {
            border: round $accent;
            &:hover {
                border: round $accent 50%;
            }
        }
        
        &:focus SelectCurrent > #label {
            text-style: $button-focus-text-style;
        }
        
        SelectCurrent > .arrow {
            margin-top: 1;
        }
    }
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Forces compact layout for listed options
        if not self.compact:
            self.compact = True