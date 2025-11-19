import asyncio
from pathlib import Path

from textual.theme import Theme

from textual_neon import NeonApp, Settings, Paths, LoadingScreen, DoneScreen, ScreenData
from panelizer.tui import HomeScreen
from panelizer.tui import PanelizerLaunchScreen


class Panelizer(NeonApp):
    """
    The main app class for the Panelizer, a textual-based terminal user interface
    for batch-fitting images onto single-color backgrounds.
    Inherits from NeonApp and implements features from textual_neon, textual_fspicker.
    """
    TITLE = "Panelizer"
    SUB_TITLE = "Batch-fit your images onto single-color backgrounds"
    MIN_ROWS = 34
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
        accent="#009ef5",
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
            data_from_result=lambda result: ScreenData(
                source="launch",
                payload=None
            ),
        )
        # noinspection PyUnusedLocal
        async def process_file_demo(file_path: str) -> bool:
            await asyncio.sleep(0.01)
            return True
        self.state_machine.register(
            "home",
            screen_class=HomeScreen,
            next_state="loading",
            fallback=None,
            validate=lambda result: bool(result),
            data_from_result=lambda result: ScreenData(
                source="home",
                payload=result["selected_files"],
                payload_names=list(map(lambda path: path.split("/")[-1], result["selected_files"])),
                function=process_file_demo,
            ),
        )
        self.state_machine.register(
            "loading",
            screen_class=LoadingScreen,
            next_state=lambda result: "done" if result[0] == "continue" else "home",
            fallback=None,
            validate=lambda result: result in [("continue", True), ("cancel", False), ("cancel", True)],
            data_from_result=lambda result: ScreenData(
                source="loading",
                payload=result
            ),
        )
        self.state_machine.register(
            "done",
            screen_class=DoneScreen,
            next_state=lambda result: result,
            fallback=None,
            validate=lambda result: result == "home" or result is None,
            data_from_result=lambda result: ScreenData(
                source="done",
                payload=result
            ),
        )

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
