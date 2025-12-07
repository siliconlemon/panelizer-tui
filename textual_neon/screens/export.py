from pathlib import Path
from typing import Union, cast

from textual import on
from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.css.query import NoMatches
from textual.screen import Screen

from textual_neon.dialogs.dir_select import DirSelectDialog
from textual_neon.utils.paths import Paths
from textual_neon.utils.screen_data import ScreenData
from textual_neon.widgets.inert_label import InertLabel
from textual_neon.widgets.neon_button import NeonButton
from textual_neon.widgets.neon_footer import NeonFooter
from textual_neon.widgets.neon_header import NeonHeader

DEFAULT_ART = """
 █████  ██     ██        ██████   ██████  ███   ██ ███████ ██
██   ██ ██     ██        ██   ██ ██    ██ ████  ██ ██      ██
███████ ██     ██        ██   ██ ██    ██ ██ ██ ██ █████   ██
██   ██ ██     ██        ██   ██ ██    ██ ██  ████ ██        
██   ██ ██████ ██████    ██████   ██████  ██   ███ ███████ ██
"""


class ExportScreen(Screen[str | None]):
    """
    An extension of the DoneScreen that lets the user export one or more files into a subdir.

    The `ScreenData.payload` for this screen MUST be a list
    of (filename, content) tuples, where content is [str | bytes]:
    [
        ("file1.csv", "...csv string..."),
        ("chart.png", b"...image bytes..."),
        ("log.txt", "File 3 content")
    ]
    """
    DEFAULT_CSS = """
    ExportScreen {
        align: center middle;
        layout: vertical;

        Container#wrapper {
            width: 100%;
            height: auto;
            margin: 1 0;
            align: center middle;

            Container#art {
                width: auto;
                height: auto;
                text-align: center;

                InertLabel {
                    color: $foreground;
                }
            }
        }
        InertLabel#text {
            width: 100%;
            height: auto;
            text-align: center;
            margin: 0 0 2 0;
            color: $foreground 80%;
        }

        Horizontal.buttons-container {
            layout: horizontal;
            height: 3;
            min-height: 3;
            max-height: 3;
            width: 100%;
            align: center middle;

            NeonButton#export-to-dir {
                width: auto;
                min-width: 46; 
                margin: 0 2 0 2;
            }
            NeonButton#home, NeonButton#quit {
                width: auto;
                min-width: 22;
                margin: 0 2 0 2;
            }   
        }

        Horizontal#export-container {
            display: none;
            margin: 1 0 0 0;
        }

        Horizontal#back-and-quit-container {
            margin: 0 0 1 0;
        }
    }
    """

    # noinspection PyShadowingBuiltins
    def __init__(
            self,
            data: ScreenData | None = None,
            *,
            text: str | None = None,
            export_dir: str | Path | None = None,
            go_back_screen: tuple[str, str] | None = ("Home", "home"),
            dialog_title: str = "Pick Export Directory",
            subdir_name: str = "export",
            ascii_art: str | None = None,
            **kwargs
    ):
        super().__init__(**kwargs)
        self.data = data
        self.go_back_screen = go_back_screen
        self.dialog_title = dialog_title
        self.base_dirname = subdir_name
        self.ascii_art = ascii_art or DEFAULT_ART

        self.export_payloads: list[tuple[str, Union[str, bytes]]] | None = None
        self.has_exported = False

        if export_dir:
            self.export_path = Path(export_dir)
        else:
            self.export_path = Paths.documents()

        if (self.data and self.data.payload and
                isinstance(self.data.payload, list) and
                len(self.data.payload) > 0):
            self.export_payloads = cast(
                list[tuple[str, str | bytes]],
                cast(object, self.data.payload)
            )

        if self.export_payloads:
            count = len(self.export_payloads)
            s = "s" if count > 1 else ""
            self.text = text or f"Aggregation complete. You can now export {count} file{s}."
        else:
            self.text = text or "You can close the terminal now."

    def compose(self) -> ComposeResult:
        yield NeonHeader()
        with Container(id="wrapper"):
            with Container(id="art"):
                yield InertLabel(self.ascii_art)
        yield InertLabel(self.text, id="text")

        with Horizontal(id="export-container", classes="buttons-container"):
            yield NeonButton(
                "Export to Directory...",
                id="export-to-dir",
                classes="buttons",
                variant="primary",
                disabled=True,
            )

        # noinspection DuplicatedCode
        with Horizontal(id="back-and-quit-container", classes="buttons-container"):
            if self.go_back_screen is not None:
                yield NeonButton(
                    f"Back to {self.go_back_screen[0]}",
                    id="home",
                    variant="primary",
                )
            yield NeonButton(
                f"Quit {self.app.TITLE}",
                id="quit",
                variant="primary",
            )
        yield NeonFooter()

    def on_mount(self) -> None:
        """Validate payload and enable export button if data exists."""
        if self.export_payloads:
            try:
                export_container = self.query_one("#export-container", Horizontal)
                export_container.display = True
                export_btn = self.query_one("#export-to-dir", NeonButton)
                export_btn.disabled = False
            except NoMatches:
                pass

    @staticmethod
    def _get_unique_path(target_path: Path) -> Path:
        """
        Checks if a path exists. If so, appends (2), (3), etc.
        Works for both files and directories.

        Example:
        ::
            .../_export.csv -> .../_export(2).csv
            .../export/ -> .../export(2)/
        """
        if not target_path.exists():
            return target_path

        parent = target_path.parent
        is_dir = target_path.is_dir() or not target_path.suffix

        stem = target_path.name
        suffix = ""
        if not is_dir:
            stem = target_path.stem
            suffix = target_path.suffix

        counter = 2
        while True:
            new_name = f"{stem}({counter}){suffix}"
            new_path = parent / new_name
            if not new_path.exists():
                return new_path
            counter += 1

    async def _handle_export(self) -> None:
        """Handle the directory select dialog and writing all export files."""
        if not self.export_payloads or self.has_exported:
            return

        try:
            export_btn = self.query_one("#export-to-dir", NeonButton)
            export_btn.disabled = True
            export_btn.label = "Exporting..."
        except NoMatches:
            self.notify("Could not find export button.", severity="error")
            return

        dialog_title = self.dialog_title
        base_dirname = self.base_dirname
        dialog_title += f" (subdir '{base_dirname}/' will be created)"
        export_dir: str | None = await self.app.push_screen_wait(
            DirSelectDialog(location=self.export_path, title=dialog_title)
        )

        if not export_dir:
            export_btn.disabled = False
            export_btn.label = "Export to Directory..."
            return

        try:
            export_base_path = Path(export_dir)
            base_target_dir = export_base_path / base_dirname
            final_target_dir = base_target_dir
            if base_target_dir.exists():
                filenames_to_write = {filename for filename, _ in self.export_payloads}
                has_overlap = False
                for existing_file in base_target_dir.iterdir():
                    if existing_file.is_file() and existing_file.name in filenames_to_write:
                        has_overlap = True
                        break
                if has_overlap:
                    final_target_dir = self._get_unique_path(base_target_dir)

            target_dir = final_target_dir
            target_dir.mkdir(parents=True, exist_ok=True)

            for filename, content in self.export_payloads:
                target_file_path = target_dir / filename
                if isinstance(content, str):
                    with target_file_path.open("w", encoding="utf-8") as f:
                        f.write(content)
                elif isinstance(content, bytes):
                    with target_file_path.open("wb") as f:
                        f.write(content)

            s = "s" if len(self.export_payloads) > 1 else ""
            self.notify(
                f"Exported {len(self.export_payloads)} file{s} to: {target_dir.as_posix()}",
                title="Export Complete",
                severity="information"
            )
            self.has_exported = True
            export_btn.label = "Exported Successfully!"

        except Exception as e:
            self.notify(
                f"Error exporting files: {e}",
                title="Export Error",
                severity="error"
            )
            if not self.has_exported:
                export_btn.disabled = False
                export_btn.label = "Export to Directory..."

    @on(NeonButton.Pressed)
    def button_pressed(self, event: NeonButton.Pressed) -> None:
        """Handle all button presses on this screen."""
        if event.button.id == "home":
            self.dismiss(self.go_back_screen[1])
        elif event.button.id == "quit":
            self.app.exit()
        elif event.button.id == "export-to-dir":
            self.run_worker(self._handle_export())
