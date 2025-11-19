from typing import override

from textual.geometry import Size

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

    @override
    def get_content_width(self, container: Size, viewport: Size) -> int:
        """
        Overrides internal button label handling to make the SettingsButtons 2 symbols narrower than usual.
        """
        width = super().get_content_width(container, viewport)
        return width - 2 if width >= 4 else width