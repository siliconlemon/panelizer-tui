from pathlib import Path

import textual
from textual.app import ComposeResult
from textual.containers import Container
from textual.events import Resize
from textual.geometry import Size
from textual.message import Message
from textual.screen import Screen
from textual.widgets import Header

from textual_neon.widgets.neon_header import NeonHeader
from textual_neon.widgets.neon_footer import  NeonFooter
from textual_neon.utils import AsciiPainter
from textual_neon.widgets.inert_label import InertLabel
from textual_neon.widgets.neon_button import NeonButton


class LaunchScreen(Screen[bool]):
    """
    A customizable launch screen with ASCII art display and enter/exit buttons.

    This screen automatically scales ASCII art based on terminal size and provides
    a clean entry point for applications. Subclass this to customize the ASCII art,
    colors, and asset directory for your own application.

    To customize:
    - Override `ASCII_ART_DIR` to point to your assets directory
    - Override `ASCII_ART_VARIANTS` with your own ASCII art files (width, height, filename)
    - Override `DEFAULT_ASCII_ART` to set your preferred fallback
    - Override `ASCII_PAINTER_COLORMAP` to define custom character-color mappings

    Usage:
    ::
        from pathlib import Path
        from textual_neon import LaunchScreen
        ...
        class MyLaunchScreen(LaunchScreen):
            ASCII_ART_DIR = Path(__file__).parent.parent.parent.parent / "assets"
            DEFAULT_ASCII_ART = (50, 25, "logo-medium.txt")
            ASCII_ART_VARIANTS = [
                (28, 15, "icon-grayscale-28.txt"),
                (30, 16, "icon-grayscale-30.txt"),
                (40, 22, "icon-grayscale-40.txt"),
                (50, 27, "icon-grayscale-50.txt"),
                (60, 33, "icon-grayscale-60.txt"),
                (70, 38, "icon-70-17.txt"),
            ]
            ASCII_PAINTER_COLORMAP = {
                "*": "#b2b2b2",
                "@": "#ffffff",
                "%": "#a8d6e5",
                "i": "#6b92bb",
                ":": "#577f7e",
            }
        ...
        # Registering in your NeonApp
        class MyNeonApp(NeonApp):
            def __init__(self) -> None:
                ...
                self.state_machine.register(
                    "launch",
                    screen=MyLaunchScreen,
                    next_state="home",
                    validate=lambda result: result is True,
                    args_from_result=lambda result: (),
                )
    """
    DEFAULT_CSS = """
    LaunchScreen {
        align: center middle;
        layout: vertical;

        Container#main {
            height: 100%;
            max-height: 50;
            align: center middle;
            width: 100%;
            height: 1fr;
            layout: vertical;
            /*background: #222233;*/
        }

        Container#alignment {
            width: 100%;
            height: 1fr;
            padding: 3 8;
            layout: horizontal;
            align: center middle;
        }

        Container#art-container {
            align: center middle;
        }

        Container#art {
            text-align: center;
        }

        Container#buttons {
            layout: horizontal;
            height: 3;
            min-height: 3;
            max-height: 3;
            width: 100%;
            align: center middle;
            margin-bottom: 1;
        }

        NeonButton.launch-btn {
            width: auto;
            width: 20;
            margin: 0 2;
        }
    }
    """
    ESCAPE_TO_MINIMIZE = True

    ASCII_ART_DIR = Path(__file__).parent.parent / "assets"
    ASCII_ART_CACHE: dict[str, str] = {}
    DEFAULT_ASCII_ART = (70, 17, "icon-70-17.txt")
    ASCII_ART_VARIANTS = [
        (70, 17, "icon-70-17.txt"),
    ]
    ASCII_PAINTER_COLORMAP = {
        "█": "#ffffff",
        "╱": "#23c47d",
    }

    class DismissRequested(Message):
        """Message sent when the screen should be dismissed."""
        def __init__(self, should_enter: bool) -> None:
            super().__init__()
            self.should_enter = should_enter

    def __init__(self, *, enter_label: str = "Enter", exit_label: str = "Exit", **kwargs):
        super().__init__(**kwargs)
        self.enter_label = enter_label
        self.exit_label = exit_label
        if not self.ASCII_ART_CACHE:
            asset_dir = self.ASCII_ART_DIR
            for _, _, filename in self.ASCII_ART_VARIANTS:
                if filename not in self.ASCII_ART_CACHE:
                    asset_path = asset_dir / filename
                    try:
                        with asset_path.open("r", encoding="utf-8") as f:
                            raw_art = f.read()
                        colorized_art = AsciiPainter.paint(ascii_string=raw_art, color_map=self.ASCII_PAINTER_COLORMAP)
                        self.ASCII_ART_CACHE[filename] = colorized_art
                    except Exception as e:
                        self.ASCII_ART_CACHE[filename] = f"Error loading {filename}:\n{e}"
                        raise e

    def on_mount(self) -> None:
        self._update_layout(self.size)

    def on_resize(self, event: Resize) -> None:
        self._update_layout(event.size)

    def compose(self) -> ComposeResult:
        yield NeonHeader()
        with Container(id="main"):
            with Container(id="alignment"):
                with Container(id="art-container"):
                    yield InertLabel(id="art")
            with Container(id="buttons"):
                yield NeonButton(self.enter_label, id="enter", classes="launch-btn", variant="primary")
                yield NeonButton(self.exit_label, id="exit", classes="launch-btn", variant="primary")
        yield NeonFooter(id="footer")

    async def on_button_pressed(self, event: textual.widgets.Button.Pressed) -> None:
        """Handles enter/exit button presses."""
        if event.button.id == "enter":
            self.post_message(self.DismissRequested(should_enter=True))
        elif event.button.id == "exit":
            self.post_message(self.DismissRequested(should_enter=False))
        event.stop()

    def on_launch_screen_dismiss_requested(self, message: DismissRequested) -> None:
        """Handle dismissal request from button press."""
        self.dismiss(message.should_enter)

    def _pick_fitting_ascii(self, cols: int, rows: int) -> tuple[int, int, str]:
        """Picks the largest ASCII art that will fit in cols×rows."""
        best = self.DEFAULT_ASCII_ART
        for width, height, filename in self.ASCII_ART_VARIANTS:
            if width <= cols and height <= rows:
                best = (width, height, filename)
            else:
                break
        return best

    def _update_ascii_art(self, filename: str) -> None:
        """Updates ASCII art label with new ASCII art."""
        art = self.ASCII_ART_CACHE.get(filename)
        ascii_label = self.query_one("#art", InertLabel)
        if art:
            ascii_label.update(art)
        else:
            ascii_label.update(f"[Error: ASCII for '{filename}' not cached!]")

    def _update_layout(self, size: Size) -> None:
        """Updates sizes/layout of the ASCII art area after a resize."""
        buttons_container = self.query_one("#buttons")
        buttons_height = buttons_container.size.height
        buttons_margin_vert = buttons_container.styles.margin.top + buttons_container.styles.margin.bottom
        footer = self.query_one("#footer")
        footer_height = footer.size.height
        footer_margin_vert = footer.styles.margin.top + footer.styles.margin.bottom

        alignment_container = self.query_one("#alignment")
        container_padding = alignment_container.styles.padding
        padding_vert = container_padding.top + container_padding.bottom
        padding_hor = container_padding.left + container_padding.right

        available_height = max(0, size.height - padding_vert - buttons_height \
                               - buttons_margin_vert - footer_height - footer_margin_vert - 1)
        available_width = max(0, size.width - padding_hor)

        width, height, filename = self._pick_fitting_ascii(available_width, available_height)
        art_container = self.query_one("#art-container")
        art_container.styles.width = width
        art_container.styles.height = height
        self._update_ascii_art(filename)
