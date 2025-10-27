"""
panelizer.tui
===================

This package contains all UI-related components for interacting with the user.
Initially, it's CLI-based (Rich/Textual), helping users select input/output
directories and flowing through the processing pipeline.
"""

from .screens import *

__all__ = []
__all__.extend(screens.__all__)