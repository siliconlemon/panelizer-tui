from typing import Iterable, override

from rich.console import RenderableType
from textual.widgets import Select
# noinspection PyProtectedMember
from textual.widgets._select import SelectType


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

    @override
    def set_options(self, options: Iterable[tuple[RenderableType, SelectType]]) -> None:
        options_formatted = map(
            lambda idx: (
                f" {idx[0].strip()} " if isinstance(idx[0], str) else idx[0], str(idx[1]),
            ),
            options,
        )
        super().set_options(options_formatted)