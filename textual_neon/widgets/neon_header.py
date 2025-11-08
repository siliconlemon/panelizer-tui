from textual.widgets import Header


class NeonHeader(Header, inherit_css=True):
    """A skin for textual's native Header widget."""
    DEFAULT_CSS = """
    NeonHeader {
        max-height: 1;
        background: transparent !important;
    }
    HeaderIcon {
        color: $foreground 50%;
    }
    """
    def __init__(self, show_clock: bool = False, *, icon="●", **kwargs):
        super().__init__(show_clock=show_clock, icon=icon, **kwargs)