from textual_fspicker.file_dialog import BaseFileDialog


class FileSelectDialog(BaseFileDialog, inherit_css=True):
    """A skin for the BaseFileDialog class from textual-fspicker, selects a single file."""
    DEFAULT_CSS = """
    FileSelect {

        OptionList {
            background: transparent;
            border: round $accent 50%;
            &:focus-within, &:hover {
                border: round $accent;
            }
        }

        InputBar {
            padding: 0;
            margin: 0;
        }

        Dialog {
            border: round $accent 50%;
            padding: 0;
        }

        SelectDirectory {
            & .option-list--option {
                padding: 0;
            }   
        }

        CurrentDirectory {
            color: $text;
            border: round $accent 50%;
        }
        
        Input {
            margin-left: 2;
            padding: 0 1 0 1;
        }

        & Input {
            color: $text;
            border: round $accent 50%;
            background: transparent;
        }

        & Input:focus, & Input:hover {
            color: $text;
            border: round $accent;
            background: transparent;
        }

        Button#select {
            padding: 0 1;
            margin-left: 2;
            margin-right: 2;
        }

        Button#cancel {
            padding: 0 1;
            margin-right: 2;
        }

        Button#select, Button#cancel {
            height: auto;
            min-width: 8;
            text-align: center;
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
    }
    """
