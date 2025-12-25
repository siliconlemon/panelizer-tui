from pathlib import Path

from textual.theme import Theme

from panelizer.tui import HomeScreen
from panelizer.tui import PanelizerLaunchScreen
from textual_neon import NeonApp, Settings, Paths, ScreenData


class Panelizer(NeonApp):
    """
    The main app class for the Panelizer.
    Migrated to Controller Pattern: Launch -> Home.
    Home handles the Loading/Done cycle internally.
    """
    TITLE = "Panelizer"
    SUB_TITLE = "Batch-fit your images onto single-color backgrounds"
    MIN_ROWS = 40
    MIN_COLS = 90
    SCREENS = {
        "launch": PanelizerLaunchScreen,
        "home": HomeScreen,
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
        self.state_machine.register(
            "home",
            screen_class=HomeScreen,
            next_state=None,
            fallback=None,
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
        s.register_default("img_pad_left", 4)
        s.register_default("img_pad_right", 4)
        s.register_default("img_pad_top", 3)
        s.register_default("img_pad_bottom", 3)
        s.register_default("img_pad_uniform", 2)

        s.register_default("canvas_height", "2500")
        s.register_default(
            "canvas_height_options",
            [
                ("2000px", "2000"),
                ("2500px", "2500"),
                ("3000px", "3000"),
                ("4000px", "4000"),
                ("5000px", "5000"),
            ]
        )

        s.register_default("canvas_ratio", "3:4")
        s.register_default(
            "canvas_ratio_options",
            [
                ("Portrait (3:4)", "3:4"),
                ("Portrait (4:5)", "4:5"),
                ("Standard (2:3)", "2:3"),
                ("Vertical (9:16)", "9:16"),
            ]
        )

        s.register_default("background_color", "white")
        s.register_default(
            "background_color_options",
            [
                ("White", "white"),
                ("Light Gray", "lightgray"),
                ("Dark Gray", "darkgray"),
                ("Black", "black")
            ]
        )

        s.register_default("layout", "framing")
        s.register_default(
            "layout_options",
            [
                ("Framing", "framing"),
                ("Uniform Border", "uniform")
            ]
        )

        s.register_default("uniform_border_orientation", "inward")
        s.register_default(
            "uniform_border_orientation_options",
            [
                ("Inward (Crop Edges)", "inward"),
                ("Outward (Add Border)", "outward")
            ]
        )

        s.register_default("uniform_border_enforcement", "3:4")
        s.register_default(
            "uniform_border_enforcement_options",
            [
                ("No size enforcement", "none"),
                ("Portrait (3:4)", "3:4"),
                ("Portrait (4:5)", "4:5"),
            ]
        )

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