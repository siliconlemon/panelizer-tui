from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Checkbox
from pathlib import Path

class FileSelectDialog(ModalScreen[list[str] | None]):
    def __init__(self, folder: Path, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.folder = Path(folder)

    def compose(self):
        with Vertical(id="file-list", classes="scrollable"):
            for file_path in sorted(self.folder.iterdir()):
                if file_path.is_file():
                    yield Checkbox(file_path.name, id=str(file_path))
        yield Button("OK", id="ok")
        yield Button("Cancel", id="cancel")

    async def on_button_pressed(self, event):
        if event.button.id == "ok":
            selected_files = [
                checkbox.id
                for checkbox in self.query(Checkbox)
                if checkbox.value
            ]
            await self.dismiss(selected_files)
        elif event.button.id == "cancel":
            await self.dismiss(None)