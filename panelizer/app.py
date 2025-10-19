"""
Main TUI entrypoint for panelizer-tui
Run this directly to launch the app.
"""

from panelizer.tui import PanelizerTUI

def terminal_entry():
    app = PanelizerTUI()
    app.run()

if __name__ == "__main__":
    terminal_entry()