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
        # self.selected_input_dir: Path | None = None

        self.state_machine.register(
            "launch",
            screen="launch",
            next_state="home",
            validate=lambda path: isinstance(path, Path) and path.exists(),
            args_from_result=lambda path: (path,),
        )
        self.state_machine.register(
            "home",
            screen=HomeScreen,
            next_state=None,
            fallback="launch",
            validate=lambda result: bool(result),
            args_from_result=lambda result: (result,),
        )
