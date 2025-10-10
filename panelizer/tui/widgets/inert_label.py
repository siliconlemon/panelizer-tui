from textual.widgets import Label


class InertLabel(Label):
    """A label with disallowed user selection."""
    ALLOW_SELECT = False
    def __init__(
        self,
        content: str = "",
        **kwargs
    ):
        super().__init__(content, **kwargs)