from pathlib import Path

from textual.theme import Theme

from textual_neon import NeonApp, Settings, Paths, LoadingScreen, DoneScreen
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
        "loading": LoadingScreen,
        "done": DoneScreen,
    }
    DEFAULT_THEME = Theme(
        name="default",
        primary="#36c8de",
        secondary="#98a1a5",
        accent="#4d84f5",
        foreground="#c0c5cd",
        background="#1e1e1e",
        success="#63bd4a",
        warning="#eba96b",
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

        self.settings = Settings(config_dir=Path("./settings"))
        self._register_defaults()
        self.settings.load()
        self._check_saved_theme()

        self.state_machine.register(
            "launch",
            screen_class=PanelizerLaunchScreen,
            next_state="home",
            fallback=None,
            validate=lambda result: result is True,
        )
        self.state_machine.register(
            "home",
            screen_class=HomeScreen,
            next_state="loading",
            fallback=None,
            validate=lambda result: bool(result),
            args_from_result=lambda result: (
                result["selected_files"],
                list(map(lambda path: path.split("/")[-1], result["selected_files"])),
                lambda file_path: f"{file_path.split('/')[-1]} processed"
            ),
        )
        self.state_machine.register(
            "loading",
            screen_class=LoadingScreen,
            next_state=lambda result: "done" if result[0] == "continue" else "home",
            fallback=None,
            validate=lambda result: result in [("continue", True), ("cancel", False), ("cancel", True)],
            args_from_result=lambda result: (),
        )
        self.state_machine.register(
            "done",
            screen_class=DoneScreen,
            next_state=lambda result: result,
            fallback=None,
            validate=lambda result: result == "home" or result is None,
        )

    def _check_saved_theme(self) -> None:
        if hasattr(self, "settings"):
            theme = self.settings.get("theme")
            if theme:
                self.theme = self.settings.get("theme")
                return
        self.theme = "default"

    def watch_theme(self, old_theme: str, new_theme: str) -> None:
        if new_theme in self.available_themes:
            if hasattr(self, "settings") and not new_theme == self.settings.get("theme"):
                self.settings.set("theme", new_theme)
                self.settings.save()
        else:
            self.theme = old_theme

    def _register_defaults(self) -> None:
        """
        Central place to define all default values for the app.
        These are the "factory settings."
        """
        s = self.settings
        s.register_default("theme", "default")
        s.register_default("start_dir", Paths.pictures().as_posix())
        s.register_default("allowed_extensions", ["jpg", "jpeg", "png"])
        s.register_default("img_pad_left", 8)
        s.register_default("img_pad_right", 8)
        s.register_default("img_pad_top", 5)
        s.register_default("img_pad_bottom", 5)
        s.register_default(
            "background_color_options",
            [
                ("White", "white"),
                ("Light Gray", "lightgray"),
                ("Dark Gray", "darkgray"),
                ("Black", "black"),
            ],
        )
        s.register_default("background_color", "white")
        s.register_default("split_wide_active", False)
        s.register_default("stack_landscape_active", False)


def terminal_entry():
    """
    The main TUI entrypoint for panelizer-tui
    Run this directly to launch the app.
    """
    app = Panelizer()
    app.run()


if __name__ == "__main__":
    terminal_entry()
