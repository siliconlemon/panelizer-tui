from typing import Literal

from textual.geometry import Size
from textual.widgets import Button
from typing_extensions import override

DefaultsButtonVariant = Literal["default", "save", "restore", "reset"]
"""A literal defining which variants the NeonButton is prepared for."""

DEFAULTS_BUTTON_VARIANTS = {"default", "save", "restore", "reset"}

class DefaultsButton(Button, inherit_css=False):
    """A skin for textual's native button widget. Used for the save, restore or reset actions."""
    DEFAULT_CSS = """
    DefaultsButton {
        color: $foreground;
        border: round $foreground 70%;
        background: transparent;
        height: auto;
        min-width: 8;
        width: auto;
        text-align: center;
        
        &:focus {
            text-style: $button-focus-text-style;
            border: round $accent;
        }
        &:hover {
            color: $foreground 80%;
            border: round $accent;
        }
        &:focus:hover {
            border: round $accent 70%;
        }
        &.-active {
            color: $foreground 40%;
            border: round $accent 40%;
        }
        &:disabled {
            color: $foreground 40%;
            border: round $accent 40%;
        }
        
        &.-save {
            &:focus {
                color: $text-success;
                border: round $success;
            }
            &:hover {
                color: $foreground 80%;
                border: round $success;
            }
            &:focus:hover {
                color: $text-success 70%;
                border: round $success 70%;
            }
            &.-active {
                color: $text-success 40%;
            }
            &:disabled {
                color: $text-success 40%;
            }
        }
        
        &.-restore {
            &:focus {
                color: $text-warning;
                border: round $warning;
            }
            &:hover {
                color: $foreground 80%;
                border: round $warning;
            }
            &:focus:hover {
                color: $text-warning 70%;
                border: round $warning-lighten-2 70%;
            }
            &.-active {
                color: $text-warning 40%;
            }
            &:disabled {
                color: $text-warning 40%;
            }
        }

        &.-reset {
            &:focus {
                color: $text-error;
                border: round $error;
            }
            &:hover {
                color: $foreground 80%;
                border: round $error;
            }
            &:focus:hover {
                color: $text-error 70%;
                border: round $text-error 70%;
            }
            &.-active {
                color: $text-error 40%;
            }
            &:disabled {
                color: $text-error 40%;
            }
        }
    }
    """

    def __init__(self, label: str, *, variant: DefaultsButtonVariant, **kwargs):
        super().__init__(f" {label.strip()} ", **kwargs)
        self.variant = self.validate_variant(variant)

    @override
    def validate_variant(self, variant: str) -> str:
        """
        A custom variant validator for when DefaultsButton variants differ from NeonButton variants.
        """
        if variant not in DEFAULTS_BUTTON_VARIANTS:
            raise ValueError(
                f"Valid DefaultsButton variants are {list(DEFAULTS_BUTTON_VARIANTS)}. Current variant: {variant}"
            )
        return variant

    @override
    def get_content_width(self, container: Size, viewport: Size) -> int:
        """
        Overrides internal button label handling to make the DefaultsButtons 2 symbols narrower than usual.
        """
        width = super().get_content_width(container, viewport)
        return width - 2 if width >= 4 else width
