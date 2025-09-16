"""
Main TUI entrypoint for panelizer-tui
Run this directly to launch the app.
"""

from panelizer.tui import PanelizerTUI

def terminal_entry():
    app = PanelizerTUI()
    response = app.run()
    print(response)

if __name__ == "__main__":
    terminal_entry()