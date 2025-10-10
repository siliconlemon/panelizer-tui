"""
A Panelizer TUI package containing custom widgets based on different widgets from `textual`.
"""

from .button import Button
from .complete_input import CompleteInput
from .complete_input_grid import CompleteInputGrid
from .simple_select import CompleteSelect
from .defaults_button import DefaultsButton
from .defaults_palette import DefaultsPalette
from .inert_label import InertLabel
from .toggle import Toggle

__all__ = [
    "Button",
    "CompleteInput",
    "CompleteInputGrid",
    "CompleteSelect",
    "DefaultsButton",
    "DefaultsPalette",
    "InertLabel",
    "Toggle",
]