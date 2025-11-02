from textual_fspicker.file_dialog import BaseFileDialog


class FileSelectDialog(BaseFileDialog, inherit_css=True):
    """
    A skin for the BaseFileDialog class from textual-fspicker, selects a single file.

    Usage:
    ::
        async def on_button_pressed(self, event: textual.widgets.Button.Pressed) -> None:
            match event.button.id:
                case "pick-file-btn":
                    self.run_worker(self._pick_file_worker, exclusive=True)
                    event.stop()
        ...
        async def _pick_file_worker(self) -> None:
            selected = await self.app.push_screen_wait(FileSelectDialog(location=self.selected_path))
            if selected:
                self.selected_file = Path(selected)
                self._update_file_display()
        ...
    """
    DEFAULT_CSS = """
    FileSelectDialog {

        OptionList {
            background: transparent;
            border: round $foreground 70%;
            &:focus-within, &:hover {
                border: round $primary;
            }
        }

        InputBar {
            padding: 0;
            margin: 0;
        }

        Dialog {
            border: round $foreground 60%;
            border-title-color: $foreground 70%;
            padding: 0;
        }

        SelectDirectory {
            & .option-list--option {
                padding: 0;
            }   
        }

        CurrentDirectory {
            color: $text;
            border: round $foreground 70%;
        }
        
        Input {
            margin-left: 2;
            padding: 0 1 0 1;
        }

        & Input {
            color: $text;
            border: round $foreground 70%;
            background: transparent;
        }

        & Input:focus, & Input:hover {
            color: $text;
            border: round $primary;
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
