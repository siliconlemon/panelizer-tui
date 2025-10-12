from pathlib import Path
from typing import Optional

import textual
from textual.app import ComposeResult
from textual.containers import Container
from textual.events import Resize
from textual.geometry import Size
from textual.screen import Screen
from textual.widgets import Header

from textual_neon import NeonButton, InertLabel, NeonDialog
from textual_neon import AsciiPainter
from textual_neon import DirSelect


class LaunchScreen(Screen[Optional[Path]]):
    CSS_PATH = ["../css/launch.tcss"]
    ESCAPE_TO_MINIMIZE = True
    DEFAULT_ASCII_ART = (40, 21, "icon-grayscale-40.txt")
    ASCII_ART_CACHE: dict[str, str] = {}
    ASCII_ART_VARIANTS = [
        (28, 15, "icon-grayscale-28.txt"),
        (30, 16, "icon-grayscale-30.txt"),
        (40, 22, "icon-grayscale-40.txt"),
        (50, 27, "icon-grayscale-50.txt"),
        (60, 33, "icon-grayscale-60.txt"),
        (70, 38, "icon-grayscale-70.txt"),
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.ASCII_ART_CACHE:
            color_map = {
                "*": "#b2b2b2",
                "@": "#ffffff",
                "%": "#a8d6e5",
                "i": "#6b92bb",
                ":": "#577f7e",
            }
            asset_dir = Path(__file__).parent.parent.parent.parent / "assets"
            for _, _, filename in self.ASCII_ART_VARIANTS:
                if filename not in self.ASCII_ART_CACHE:
                    asset_path = asset_dir / filename
                    try:
                        with asset_path.open("r", encoding="utf-8") as f:
                            raw_art = f.read()
                        colorized_art = AsciiPainter.paint(ascii_string=raw_art, color_map=color_map)
                        self.ASCII_ART_CACHE[filename] = colorized_art
                    except Exception as e:
                        self.ASCII_ART_CACHE[filename] = f"[Error loading {filename}: {e}]"

    def on_mount(self) -> None:
        self._update_layout(self.size)

    def on_resize(self, event: Resize) -> None:
        self._update_layout(event.size)

    def compose(self) -> ComposeResult:
        yield Header(icon="●")
        with Container(id="launch-container"):
            with Container(id="alignment-container"):
                with Container(id="ascii-art-container"):
                    yield InertLabel(id="ascii-art")
            with Container(id="button-container"):
                yield NeonButton("Pick a Directory", id="pick-dir", classes="wide-btn", variant="primary")
                yield NeonButton("Current Directory", id="current-dir", classes="wide-btn", variant="primary")

    async def _handle_directory_selection(self, start_directory: Path) -> None:
        """Opens directory picker and dismiss with selected path or None."""
        selected_directory = await self.app.push_screen_wait(
            DirSelect(location=start_directory, double_click_directories=False)
        )
        # noinspection PyAsyncCall
        self.dismiss(selected_directory or None)

    async def on_button_pressed(self, event: textual.widgets.Button.Pressed) -> None:
        """Handles directory selection buttons."""
        lookup = {
            "pick-dir": Path.home() / "Pictures",
            "current-dir": Path.cwd()
        }
        if event.button.id in lookup:
            await self._handle_directory_selection(lookup[event.button.id])

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
        ascii_label = self.query_one("#ascii-art", InertLabel)
        if art:
            ascii_label.update(art)
        else:
            ascii_label.update(f"[Error: ASCII for '{filename}' not cached!]")

    def _update_layout(self, size: Size) -> None:
        """Updates sizes/layout of the ASCII art area after a resize."""
        button_container = self.query_one("#button-container")
        button_height = button_container.size.height
        button_margin = button_container.styles.margin
        button_margin_height = button_margin.top + button_margin.bottom

        alignment_container = self.query_one("#alignment-container")
        container_padding = alignment_container.styles.padding
        padding_height = container_padding.top + container_padding.bottom
        padding_width = container_padding.left + container_padding.right

        available_height = max(0, size.height - button_height - button_margin_height - padding_height - 1)
        available_width = max(0, size.width - padding_width)

        width, height, filename = self._pick_fitting_ascii(available_width, available_height)
        art_container = self.query_one("#ascii-art-container")
        art_container.styles.width = width
        art_container.styles.height = height
        self._update_ascii_art(filename)
