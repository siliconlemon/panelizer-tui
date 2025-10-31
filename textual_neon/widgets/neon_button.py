from typing import Literal

from textual.widgets import Button
from typing_extensions import override

NeonButtonVariant = Literal["default", "primary", "success", "warning", "error"]
"""A literal defining which variants the NeonButton is prepared for."""

NEON_BUTTON_VARIANTS = {"default", "primary", "success", "warning", "error"}

class NeonButton(Button, inherit_css=False):
    """A skin for textual's native Button widget."""
    DEFAULT_CSS = """
    NeonButton {
        color: $foreground;
        border: round $foreground;
        background: transparent;
        height: auto;
        min-width: 8;
        text-align: center;
        
        &:focus {
            text-style: $button-focus-text-style;
        }
        &:hover {
            color: $foreground 70%;
            border: round $foreground 60%;
        }
        &.-active {
            color: $foreground 40%;
            border: round $foreground 30%;
        }
        &:disabled {
            color: $foreground 30%;
            border: round $foreground 20%;
        }
        
        &.-primary {
            color: $primary-lighten-1;
            border: round $primary;
            background: transparent;
            
            &:hover {
                color: $primary-lighten-1 70%;
                border: round $primary 60%;
            }
            &.-active {
                color: $primary-lighten-1 40%;
                border: round $primary 30%;
            }
            &:disabled {
                color: $primary-lighten-1 30%;
                border: round $primary 20%;
            }
        }
        
        &.-success {
            color: $success-lighten-1;
            border: round $success;
            background: transparent;
            
            &:hover {
                color: $success-lighten-1 70%;
                border: round $success 60%;
            }
            &.-active {
                color: $success-lighten-1 40%;
                border: round $success 30%;
            }
            &:disabled {
                color: $success-lighten-1 30%;
                border: round $success 20%;
            }
        }
        
        &.-warning{
            color: $warning-lighten-1;
            border: round $warning;
            background: transparent;
            
            &:hover {
                color: $warning-lighten-1 70%;
                border: round $warning 60%;
            }
            &.-active {
                color: $warning-lighten-1 40%;
                border: round $warning 30%;
            }
            &:disabled {
                color: $warning-lighten-1 30%;
                border: round $warning 20%;
            }
        }

        &.-error {
            color: $error-lighten-1;
            border: round $error;
            background: transparent;
            
            &:hover {
                color: $error-lighten-1 70%;
                border: round $error 60%;
            }
            &.-active {
                color: $error-lighten-1 40%;
                border: round $error 30%;
            }
            &:disabled {
                color: $error-lighten-1 30%;
                border: round $error 20%;
            }
        }
    }
    """

    def __init__(self, label: str, variant: NeonButtonVariant = "default", **kwargs):
        super().__init__(f" {label.strip()} ", variant, **kwargs)

    @override
    def validate_variant(self, variant: str) -> str:
        """
        A custom variant validator for when NeonButton variants might differ from Button variants.
        """
        if variant not in NEON_BUTTON_VARIANTS:
            raise ValueError(
                f"Valid NeonButton variants are {list(NEON_BUTTON_VARIANTS)}. Current variant: {variant}"
            )
        return variant

    def watch_label(self, new_label: str) -> None:
        """
        Called automatically by Textual when the `self.label` attribute changes.
        This method ensures the label is always correctly formatted.
        """
        formatted_label = f" {str(new_label).strip()} "
        if self.label != formatted_label:
            self.label = formatted_label