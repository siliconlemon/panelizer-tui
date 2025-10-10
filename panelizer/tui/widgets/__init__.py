"""
A Panelizer TUI package containing custom widgets based on different widgets from `textual`.
"""

from .defaults_button import DefaultsButton
from .defaults_palette import DefaultsPalette
from .simple_button import SimpleButton
from .simple_input import SimpleInput
from .simple_input_grid import SimpleInputGrid
from .simple_select import SimpleSelect
from .switch_button import SwitchButton

__all__ = [
    "DefaultsButton",
    "DefaultsPalette",
    "SimpleButton",
    "SimpleInput",
    "SimpleInputGrid",
    "SimpleSelect",
    "SwitchButton"
]