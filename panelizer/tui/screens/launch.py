import os
from textual.app import ComposeResult
from textual.containers import Container
from textual.widgets import Header, Label, Button
from textual.screen import Screen
from textual.events import Resize


class LaunchScreen(Screen):
    CSS_PATH = "../css/launch.tcss"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ascii_art = ""
        self.ascii_art_files = {
            80: "icon-grayscale-80.txt",
            100: "icon-grayscale-100.txt",
            120: "icon-grayscale-120.txt",
        }

    def on_mount(self) -> None:
        self.on_resize(None)

    def on_resize(self, event: Resize) -> None:
        width = event.size.width if event else self.size.width

        if width < 100:
            file_name = self.ascii_art_files[80]
        elif width < 120:
            file_name = self.ascii_art_files[100]
        else:
            file_name = self.ascii_art_files[120]

        module_dir = os.path.dirname(os.path.abspath(__file__))
        project_root_dir = os.path.dirname(os.path.dirname(os.path.dirname(module_dir)))
        file_path = os.path.join(project_root_dir, "assets", file_name)

        try:
            with open(file_path, "r") as f:
                new_art = f.read()

            label = self.query_one("#ascii-art-label", Label)
            label.update(new_art)
        except FileNotFoundError:
            self.ascii_art = f"Error: ASCII art file not found at {file_path}"
        except Exception as e:
            self.ascii_art = f"Error: {e}"

    def compose(self) -> ComposeResult:
        yield Header()
        with Container(id="launch-container"):
            yield Label("", id="ascii-art-label")
            with Container(id="button-container"):
                yield Button("📂 Pick Directory", id="pick-dir", variant="primary")
                yield Button("📝 Current Directory", id="current-dir")