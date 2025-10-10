from typing import Literal

import textual

NeonButtonVariant = Literal["default", "primary", "success", "warning", "error"]


class NeonButton(textual.widgets.Button, inherit_css=False):
    """A skin for textual's native button widget."""
    DEFAULT_CSS = """
        NeonButton {
            color: $text;
            border: round $accent;
            background: transparent;
            height: auto;
            min-width: 8;
            text-align: center;
            
            &:focus {
                text-style: $button-focus-text-style;
            }
            &:hover {
                color: $text 60%;
                border: round $accent 60%;
            }
            &.-active {
                color: $text 40%;
                border: round $accent 40%;
            }
            &:disabled {
                color: $text 30%;
                border: round $accent 30%;
            }
            
            &.-primary {
                color: $primary-lighten-1;
                border: round $primary;
                background: transparent;
                
                &:hover {
                    color: $primary-lighten-1 60%;
                    border: round $primary 60%;
                }
                &.-active {
                    color: $primary-lighten-1 40%;
                    border: round $primary 40%;
                }
                &:disabled {
                    color: $primary-lighten-1 20%;
                    border: round $primary 20%;
                }
            }
            
            &.-success {
                color: $success-lighten-1;
                border: round $success;
                background: transparent;
                
                &:hover {
                    color: $success-lighten-1 60%;
                    border: round $success 60%;
                }
                &.-active {
                    color: $success-lighten-1 40%;
                    border: round $success 40%;
                }
                &:disabled {
                    color: $success-lighten-1 20%;
                    border: round $primary 20%;
                }
            }
            
            &.-warning{
                color: $warning-lighten-1;
                border: round $warning;
                background: transparent;
                
                &:hover {
                    color: $warning-lighten-1 60%;
                    border: round $warning 60%;
                }
                &.-active {
                    color: $warning-lighten-1 40%;
                    border: round $warning 40%;
                }
                &:disabled {
                    color: $warning-lighten-1 20%;
                    border: round $warning 20%;
                }
            }

            &.-error {
                color: $error-lighten-1;
                border: round $error;
                background: transparent;
                
                &:hover {
                    color: $error-lighten-1 60%;
                    border: round $error 60%;
                }
                &.-active {
                    color: $error-lighten-1 40%;
                    border: round $error 40%;
                }
                &:disabled {
                    color: $error-lighten-1 20%;
                    border: round $error 20%;
                }
            }
        }
    """

    def __init__(
        self,
        label: str,
        variant: NeonButtonVariant = "default",
        **kwargs
    ):
        super().__init__(f" {label.strip()} ", variant, **kwargs)