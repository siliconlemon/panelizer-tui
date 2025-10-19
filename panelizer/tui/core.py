from pathlib import Path

from textual_neon import NeonApp
from .screens.home import HomeScreen
from .screens.launch import LaunchScreen


class PanelizerTUI(NeonApp):
    TITLE = "Panelizer"
    SUB_TITLE = "Batch-fit your images onto single-color backgrounds"
    SCREENS = {
        "launch": LaunchScreen,
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
