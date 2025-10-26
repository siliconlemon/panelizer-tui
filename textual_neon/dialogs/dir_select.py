from textual_fspicker import SelectDirectory


class DirSelectDialog(SelectDirectory, inherit_css=True):
    """
    A skin for the SelectDirectory class from textual-fspicker, selects a single directory.

    Usage:
    ::
        async def on_button_pressed(self, event: textual.widgets.Button.Pressed) -> None:
            match event.button.id:
                case "path-btn":
                    self.run_worker(self._select_dir_worker, exclusive=True)
                    event.stop()
        ...
        async def _select_dir_worker(self) -> None:
            new_dir = await self.app.push_screen_wait(DirSelectDialog(location=self.selected_path))
            if new_dir:
                self.selected_path = Path(new_dir)
                self._update_path_display()
        ...
        async def on_unmount(self) -> None:
            self.workers.cancel_all()
    """
    DEFAULT_CSS = """
    DirSelectDialog {
    
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
            margin-left: 2;
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
