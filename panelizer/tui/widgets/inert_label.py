from textual.widgets import Label


class InertLabel(Label, inherit_css=False):
    """A label with disallowed user selection."""
    ALLOW_SELECT = False
    DEFAULT_CSS = """
        InertLabel {
            color: $text;
            height: auto;
            width: auto;
        }
    """

    def __init__(
        self,
        content: str = "",
        **kwargs
    ):
        super().__init__(content, **kwargs)