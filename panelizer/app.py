"""
Main TUI entrypoint for panelizer-tui
Run this directly to launch the app.
"""

from textual_neon import NeonApp
from panelizer.tui.screens.home import HomeScreen
from panelizer.tui.screens.launch import PanelizerLaunchScreen


class Panelizer(NeonApp):
    TITLE = "Panelizer"
    SUB_TITLE = "Batch-fit your images onto single-color backgrounds"
    SCREENS = {
        "launch": PanelizerLaunchScreen,
        "home": HomeScreen,
    }

    def __init__(self) -> None:
        super().__init__()
        self.state_machine.register(
            "launch",
            screen="launch",
            next_state="home",
            validate=lambda result: result is True,
            args_from_result=lambda result: (),
        )
        self.state_machine.register(
            "home",
            screen=HomeScreen,
            next_state=None,
            fallback="launch",
            validate=lambda result: bool(result),
            args_from_result=lambda result: (result,),
        )


def terminal_entry():
    app = Panelizer()
    app.run()


if __name__ == "__main__":
    terminal_entry()
