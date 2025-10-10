"""
A Panelizer TUI package containing custom widgets based on different widgets from `textual`.
"""

from .defaults_button import DefaultsButton
from .defaults_palette import DefaultsPalette
from .inert_label import InertLabel
from .simple_button import SimpleButton
from .simple_input import SimpleInput
from .simple_input_grid import SimpleInputGrid
from .simple_select import SimpleSelect
from .toggle import Toggle

__all__ = [
    "DefaultsButton",
    "DefaultsPalette",
    "InertLabel",
    "SimpleButton",
    "SimpleInput",
    "SimpleInputGrid",
    "SimpleSelect",
    "Toggle"
]