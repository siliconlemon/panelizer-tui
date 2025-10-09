"""
A Panelizer TUI package containing custom widgets based on the Widget class from `textual`.
"""

from .defaults_palette import DefaultsPalette
from .input_grid import InputGrid
from .simple_select import SimpleSelect
from .switch_button import SwitchButton

__all__ = ["DefaultsPalette", "InputGrid", "SimpleSelect", "SwitchButton"]