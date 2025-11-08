from textual_neon.widgets.neon_button import NeonButton


class MinimalButton(NeonButton):
    """A minimal version of the NeonButton to be used as an attachment to larger widgets like option lists or logs."""
    DEFAULT_CSS = """
    MinimalButton {
        height: 1;
        width: auto;
        border: none !important;
        margin: 0 !important;
    }
    """