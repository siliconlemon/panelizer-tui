from typing import Literal

from textual.widgets import Button

DefaultsButtonVariant = Literal["save", "restore", "reset"]

class DefaultsButton(Button):
    """A skin for textual's native button widget. Used for the save, restore or reset actions."""

    DEFAULT_CSS = """
        DefaultsButton {
            padding: 0;
            color: $text;
            border: round $secondary;
        
            &.save:focus, &.save:hover {
                color: $success-lighten-1;
            }
            
            &.restore:focus, &.restore:hover {
                color: $warning-lighten-1;
            }
            
            &.reset:focus, &.reset:hover {
                color: $error-lighten-1;
            }
            
            &:focus, &:hover {
                color: $text;
                border: round $accent;
            }
        }
    """

    def __init__(self, **kwargs):
        self.defaults_variant = self.validate_defaults_variant(kwargs.pop("variant"))
        super().__init__(**kwargs)


    @staticmethod
    def validate_defaults_variant(variant: str) -> str:
        if variant not in DefaultsButtonVariant:
            raise ValueError(
                f"Valid DefaultsButton variants are {list(DefaultsButtonVariant)}"
            )
        return variant