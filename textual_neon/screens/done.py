from textual import on
from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.screen import Screen

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
    A simple screen to show a "Done" disclaimer and provide
    basic navigation options.
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

            NeonButton#home, NeonButton#quit {
                width: auto;
                min-width: 22;
                margin: 0 2 0 2;
            }   
        }

        Horizontal#back-and-quit-container {
            margin: 0 0 1 0;
        }
    }
    """

    # noinspection PyShadowingBuiltins
    def __init__(
            self,
            *,
            text: str | None = None,
            go_back_screen: tuple[str, str] | None = ("Home", "home"),
            ascii_art: str | None = None,
            **kwargs
    ):
        """
        Initializes the simplified DoneScreen.

        Args:
            text: The text to display (e.g., "Process Complete").
            go_back_screen: A tuple (label, screen_id) for the "Back" button.
            ascii_art: Optional ASCII art to display.
            **kwargs: Additional keyword arguments.
        """
        super().__init__(**kwargs)
        self.go_back_screen = go_back_screen
        self.ascii_art = ascii_art or DEFAULT_ART
        self.text = text or "You can close the terminal now."

    def compose(self) -> ComposeResult:
        yield NeonHeader()
        with Container(id="wrapper"):
            with Container(id="art"):
                yield InertLabel(self.ascii_art)
        yield InertLabel(self.text, id="text")

        with Horizontal(id="back-and-quit-container", classes="buttons-container"):
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

    @on(NeonButton.Pressed)
    def button_pressed(self, event: NeonButton.Pressed) -> None:
        """Handle all button presses on this screen."""
        if event.button.id == "home":
            self.dismiss(self.go_back_screen[1])
        elif event.button.id == "quit":
            self.app.exit()