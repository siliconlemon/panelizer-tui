from typing_extensions import override

from textual_neon.widgets.neon_button import NeonButton, NEON_BUTTON_VARIANTS


class PathButton(NeonButton):
    """
    A button for displaying and interacting with file paths.
    Inherits from NeonButton.
    """
    DEFAULT_CSS = """
    PathButton {
        overflow-x: hidden;
        width: 1fr;
        max-width: 100%;
        color: $foreground;
        border: round $foreground;

        &:hover {
            text-style: underline;
            color: $foreground;
        }
        &.-active {
            color: $foreground 40%;
            border: round $accent 30%;
        }
        &:disabled {
            color: $foreground 30%;
            border: round $accent 20%;
        }
    }
    """

    @override
    def validate_variant(self, variant: str) -> str:
        if variant not in NEON_BUTTON_VARIANTS:
            raise ValueError(
                f"Valid PathButton variants are {list(NEON_BUTTON_VARIANTS)}. Current variant: {variant}"
            )
        return variant