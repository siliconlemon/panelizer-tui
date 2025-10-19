from textual_fspicker.file_dialog import BaseFileDialog


class FileSelectDialog(BaseFileDialog, inherit_css=True):
    """A skin for the BaseFileDialog class from textual-fspicker, selects a single file.

    Usage:
    ::
        async def on_button_pressed(self, event: textual.widgets.Button.Pressed) -> None:
            match event.button.id:
                case "pick-file-btn":
                    self._most_recent_worker = self.app.run_worker(self._pick_file_task, exclusive=True)
                    event.stop()
        ...
        async def _pick_file_task(self) -> None:
            selected = await self.app.push_screen_wait(FileSelectDialog(location=self.selected_path))
            if selected:
                self.selected_file = Path(selected)
                self._update_file_display()
        ...
        async def on_unmount(self) -> None:
            if self._most_recent_worker and self._most_recent_worker.is_running:
                self._most_recent_worker.cancel()
    """
    DEFAULT_CSS = """
    FileSelectDialog {

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
