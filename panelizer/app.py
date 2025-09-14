"""
Main TUI entrypoint for panelizer-tui
Run this directly to launch the app.
"""

from panelizer.tui import PanelizerTui

def terminal_entry():
    app = PanelizerTui()
    app.run()

if __name__ == "__main__":
    terminal_entry()