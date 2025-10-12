from typing import Literal

from textual.geometry import Size
from textual.widgets import Button
from typing_extensions import override

DefaultsButtonVariant = Literal["save", "restore", "reset"]
"""A literal defining which variants the NeonButton is prepared for."""

DEFAULTS_BUTTON_VARIANTS = {"save", "restore", "reset"}

# FIXME: These don't appear for some reason
class DefaultsButton(Button, inherit_css=False):
    """A skin for textual's native button widget. Used for the save, restore or reset actions."""
    DEFAULT_CSS = """
    DefaultsButton {
        color: $text;
        border: round $accent 50%;
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
            color: $text 60%;
            border: round $accent;
        }
        &:focus:hover {
            border: round $accent 50%;
        }
        &.-active {
            color: $text 40%;
            border: round $accent 40%;
        }
        &:disabled {
            color: $text 30%;
            border: round $accent 30%;
        }
        
        &.-save {
            &:focus, &:hover {
                color: $success-lighten-1;
            }
            &.-active {
                color: $success-lighten-1 40%;
            }
            &:disabled {
                color: $success-lighten-1 20%;
            }
        }
        
        &.-restore {
            &:focus, &:hover {
                color: $warning-lighten-1;
            }
            &.-active {
                color: $warning-lighten-1 40%;
            }
            &:disabled {
                color: $warning-lighten-1 20%;
            }
        }

        &.-reset {
            &:focus, &:hover {
                color: $warning-lighten-1;
            }
            &.-active {
                color: $error-lighten-1 40%;
            }
            &:disabled {
                color: $error-lighten-1 20%;
            }
        }
    }
    """

    def __init__(
        self,
        label: str,
        *,
        variant: DefaultsButtonVariant,
        **kwargs
    ):
        super().__init__(f" {label.strip()} ", variant=variant, **kwargs)
        self.validate_variant(variant)

    @override
    @staticmethod
    def validate_variant(variant: str) -> str:
        if variant not in DEFAULTS_BUTTON_VARIANTS:
            raise ValueError(
                f"Valid DefaultsButton variants are {list(DEFAULTS_BUTTON_VARIANTS)}"
            )
        return variant

    @override
    def get_content_width(self, container: Size, viewport: Size) -> int:
        width = super().get_content_width(container, viewport)
        return width - 2 if width >= 4 else width