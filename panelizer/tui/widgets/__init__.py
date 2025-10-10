"""
A Panelizer TUI package containing custom widgets based on the Widget class from `textual`.
"""

from .defaults_palette import DefaultsPalette
from .simple_input import SimpleInput
from .simple_input_grid import SimpleInputGrid
from .simple_select import SimpleSelect
from .switch_button import SwitchButton

__all__ = ["DefaultsPalette", "SimpleInput", "SimpleInputGrid", "SimpleSelect", "SwitchButton"]