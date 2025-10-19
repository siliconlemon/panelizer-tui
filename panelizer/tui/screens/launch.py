from pathlib import Path

from textual_neon import LaunchScreen


class PanelizerLaunchScreen(LaunchScreen):
    """A basic launch screen based on the LaunchScreen class from textual_neon."""
    ASCII_ART_DIR = Path(__file__).parent.parent.parent.parent / "assets"
    DEFAULT_ASCII_ART = (50, 25, "logo-medium.txt")
    ASCII_ART_VARIANTS = [
        (28, 15, "icon-grayscale-28.txt"),
        (30, 16, "icon-grayscale-30.txt"),
        (40, 22, "icon-grayscale-40.txt"),
        (50, 27, "icon-grayscale-50.txt"),
        (60, 33, "icon-grayscale-60.txt"),
        (70, 38, "icon-grayscale-70.txt"),
    ]
    ASCII_PAINTER_COLORMAP = {
        "*": "#b2b2b2",
        "@": "#ffffff",
        "%": "#a8d6e5",
        "i": "#6b92bb",
        ":": "#577f7e",
    }

    def __init__(self, *, enter_label: str = "Enter", exit_label: str = "Exit", **kwargs):
        super().__init__(**kwargs)
        self.enter_label = enter_label
        self.exit_label = exit_label