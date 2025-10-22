from pathlib import Path

from textual.theme import Theme

from textual_neon import NeonApp, Preferences, Paths
from .tui import HomeScreen
from .tui import PanelizerLaunchScreen


class Panelizer(NeonApp):
    """
    The main app class for the Panelizer, a textual-based terminal user interface
    for batch-fitting images onto single-color backgrounds.
    Inherits from NeonApp and implements features from textual_neon, textual_fspicker.
    """
    TITLE = "Panelizer"
    SUB_TITLE = "Batch-fit your images onto single-color backgrounds"
    MIN_ROWS = 32
    MIN_COLS = 90
    SCREENS = {
        "launch": PanelizerLaunchScreen,
        "home": HomeScreen,
    }
    DEFAULT_THEME = Theme(
        name="default",
        primary="#36c8de",
        secondary="#98a1a5",
        accent="#ffffff",
        foreground="#c0c5cd",
        background="#1e1e1e",
        success="#63bd4a",
        warning="#ebb370",
        error="#ff524d",
        surface="#3b4252",
        panel="#17171a",
        dark=True,
        variables={
            "block-cursor-text-style": "none",
            "footer-key-foreground": "#88c0d0",
        },
    )

    def __init__(self) -> None:
        super().__init__()

        self.preferences = Preferences(config_dir=Path("./preferences"))
        self._register_defaults()
        self.preferences.load()

        self.state_machine.register(
            "launch",
            screen="launch",
            next_state="home",
            validate=lambda result: result is True,
            args_from_result=lambda result: (),
        )
        self.state_machine.register(
            "home",
            screen=HomeScreen,
            next_state=None,
            fallback="launch",
            validate=lambda result: bool(result),
            args_from_result=lambda result: (result,),
        )

    def _register_defaults(self) -> None:
        """
        Central place to define all default values for the app.
        These are the "factory settings."
        """
        p = self.preferences
        # TODO: Shouldn't the format (posix) be determined by the os in Paths?
        p.register_default("start_dir", Paths.pictures().as_posix())
        p.register_default("img_pad_left", 0)
        p.register_default("img_pad_right", 0)
        p.register_default("img_pad_top", 0)
        p.register_default("img_pad_bottom", 0)
        p.register_default("background_color", "white")
        p.register_default("split_wide_active", False)
        p.register_default("stack_landscape_active", False)


def terminal_entry():
    """
    The main TUI entrypoint for panelizer-tui
    Run this directly to launch the app.
    """
    app = Panelizer()
    app.run()


if __name__ == "__main__":
    terminal_entry()
