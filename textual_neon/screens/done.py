from textual import on
from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.screen import Screen

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


class DoneScreen(Screen[str | None]):
    """
    A simple screen to show a "Done" disclaimer and provide navigation options.
    """
    DEFAULT_CSS = """
    DoneScreen {
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
            margin: 0 0 1 0;
            color: $foreground 80%;
        }
        Horizontal#buttons {
            layout: horizontal;
            height: 3;
            min-height: 3;
            max-height: 3;
            width: 100%;
            align: center middle;
            margin-bottom: 1;
        }
        NeonButton {
            width: auto;
            min-width: 22;
            margin: 0 2;
        }
    }
    """

    # noinspection PyShadowingBuiltins
    def __init__(
            self,
            data: ScreenData | None = None,
            *,
            ascii_art: str | None = None,
            text: str | None = None,
            go_back_screen: tuple[str, str] | None = ("Home", "home"),
            name: str | None = None,
            id: str | None = None,
            classes: str | None = None,
    ):
        super().__init__(name=name, id=id, classes=classes)
        self.data = data
        self.ascii_art = ascii_art or DEFAULT_ART
        self.text = text or "You can close the terminal now."
        self.go_back_screen = go_back_screen

    def compose(self) -> ComposeResult:
        yield NeonHeader()
        with Container(id="wrapper"):
            with Container(id="art"):
                yield InertLabel(self.ascii_art)
        yield InertLabel(self.text, id="text")
        with Horizontal(id="buttons"):
            if self.go_back_screen is not None:
                yield NeonButton(
                    f"Back to {self.go_back_screen[0]}",
                    id="home",
                    variant="primary",
                )
            yield NeonButton(
                "Quit to Terminal",
                id="quit",
                variant="primary",
            )
        yield NeonFooter()

    @on(NeonButton.Pressed, "#home")
    def home_button_pressed(self) -> None:
        self.dismiss(self.go_back_screen[1])

    @on(NeonButton.Pressed, "#quit")
    def quit_button_pressed(self) -> None:
        self.dismiss(None)

    @on(NeonButton.Pressed, "#close")
    def close_button_pressed(self) -> None:
        self.app.exit()

