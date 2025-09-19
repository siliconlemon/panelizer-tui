from pathlib import Path

from textual import work
from textual.app import ComposeResult
from textual.containers import Container
from textual.events import Resize
from textual.geometry import Size
from textual.screen import Screen, ScreenResultType
from textual.widgets import Header, Label, Button
from textual_fspicker import SelectDirectory

from ...utils.ascii_painter import paint
from ..widgets.too_small import TooSmall


class LaunchScreen(Screen[ScreenResultType]):
    CSS_PATH = ["../css/launch.tcss", "../css/too_small.tcss"]
    HEADER_HEIGHT = 1
    BUTTON_AREA_HEIGHT = 2
    ASCII_ART_VARIANTS = [
        (30, 16, "icon-grayscale-40.txt"),
        (40, 22, "icon-grayscale-40.txt"),
        (50, 27, "icon-grayscale-50.txt"),
        (60, 33, "icon-grayscale-60.txt"),
        (70, 38, "icon-grayscale-70.txt"),
    ]
    DEFAULT_ASCII_ART = (40, 21, "icon-grayscale-40.txt")
    ASCII_ART_CACHE = {}
    MIN_HEIGHT_ROWS = 35
    MIN_WIDTH_COLS = 60

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
                            colorized_art = paint(ascii_string=raw_art, color_map=color_map)
                            self.ASCII_ART_CACHE[filename] = colorized_art
                    except FileNotFoundError:
                        self.ASCII_ART_CACHE[filename] = f"Error: File not found at {asset_path}"
                    except Exception as e:
                        self.ASCII_ART_CACHE[filename] = f"Error: {e}"


    async def _handle_directory_selection(self, start_directory: Path) -> None:
        selected_directory = await self.app.push_screen_wait(
            SelectDirectory(location=start_directory, double_click_directories=False)
        )
        if selected_directory:
            await self.dismiss(selected_directory)
        else:
            await self.dismiss(None)


    @work(exclusive=True)
    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "pick-dir":
            start_directory = Path.home() / "Pictures"
            await self._handle_directory_selection(start_directory)
        elif event.button.id == "current-dir":
            start_directory = Path.cwd()
            await self._handle_directory_selection(start_directory)


    def _pick_fitting_ascii(self, cols, rows):
        best = self.DEFAULT_ASCII_ART
        for width, height, filename in self.ASCII_ART_VARIANTS:
            if width <= cols and height <= rows:
                best = (width, height, filename)
            else:
                break
        return best

    def _update_ascii_art(self, filename):
        new_art = self.ASCII_ART_CACHE.get(filename)

        if new_art is not None:
            self.query_one("#ascii-art", Label).update(new_art)
        else:
            self.query_one("#ascii-art", Label).update(
                f"Error: ASCII art for file '{filename}' not found inside cache."
            )


    def _update_layout(self, size: Size) -> None:
        button_container = self.query_one("#button-container")
        button_height = button_container.size.height
        button_margin = button_container.styles.margin
        button_margin_height = button_margin.top + button_margin.bottom

        alignment_container = self.query_one("#alignment-container")
        container_padding = alignment_container.styles.padding
        padding_height = container_padding.top + container_padding.bottom

        available_height = (
                size.height
                - self.HEADER_HEIGHT
                - button_height
                - button_margin_height
                - padding_height
        )
        available_height = max(0, available_height)

        padding_width = container_padding.left + container_padding.right
        available_width = size.width - padding_width
        available_width = max(0, available_width)

        width, height, filename = self._pick_fitting_ascii(available_width, available_height)
        art_container = self.query_one("#ascii-art-container")
        art_container.styles.width = width
        art_container.styles.height = height
        self._update_ascii_art(filename)


    def _check_terminal_size(self, cols, rows):
        overlay = self.query_one(TooSmall)
        overlay.set_size(cols, rows)
        if rows < self.MIN_HEIGHT_ROWS or cols < self.MIN_WIDTH_COLS:
            overlay.display = True
        else:
            overlay.display = False


    def on_mount(self) -> None:
        ascii_art = self.query_one("#ascii-art", Label)
        ascii_art.can_focus = False
        self._update_layout(self.size)
        self._check_terminal_size(self.size.width, self.size.height)


    def on_resize(self, event: Resize) -> None:
        self._update_layout(event.size)
        self._check_terminal_size(event.size.width, event.size.height)


    def compose(self) -> ComposeResult:
        yield Header()
        with Container(id="launch-container"):
            with Container(id="alignment-container"):
                with Container(id="ascii-art-container"):
                    yield Label(id="ascii-art")
            with Container(id="button-container"):
                yield Button("Pick a Directory", id="pick-dir", variant="primary")
                yield Button("Current Directory", id="current-dir")
        yield TooSmall(
            min_height=self.MIN_HEIGHT_ROWS,
            min_width=self.MIN_WIDTH_COLS,
            classes="terminal-too-small",
            id="terminal-too-small"
        )
