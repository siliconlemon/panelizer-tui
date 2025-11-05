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
    """
    DEFAULT_CSS = """
    DirSelectDialog {
    
        OptionList {
            background: transparent;
            border: round $foreground 70%;
            &:focus-within, &:hover {
                border: round $foreground;
            }
        }
        
        InputBar {
            padding: 0;
            margin: 0;
        }
        
        Dialog {
            border: round $foreground 70%;
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
            margin-left: 2;
        }
        
        & Input {
            color: $text;
            border: round $foreground 70%;
            background: transparent;
        }
        
        & Input:focus, & Input:hover {
            color: $text;
            border: round $foreground;
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
            color: $text-primary;
            border: round $primary;
            background: transparent;
            &:hover {
                color: $text-primary 60%;
                border: round $accent;
            }
            &.-active {
                color: $text-primary 40%;
                border: round $primary 40%;
            }
            &:disabled {
                color: $text-primary 40%;
                border: round $primary 40%;
            }
            
            &.-primary {
                color: $text-primary;
                border: round $primary;
                background: transparent;
                
                &:hover {
                    color: $text-primary 60%;
                    border: round $accent;
                }
                &.-active {
                    color: $text-primary 40%;
                    border: round $primary 40%;
                }
                &:disabled {
                    color: $text-primary 40%;
                    border: round $primary 40%;
                }
            }
            
            &.-success {
                color: $text-success;
                border: round $success;
                background: transparent;
                
                &:hover {
                    color: $text-success 60%;
                    border: round $success 60%;
                }
                &.-active {
                    color: $text-success 40%;
                    border: round $success 40%;
                }
                &:disabled {
                    color: $text-success 40%;
                    border: round $primary 40%;
                }
            }
            
            &.-warning{
                color: $text-warning;
                border: round $warning;
                background: transparent;
                
                &:hover {
                    color: $text-warning 60%;
                    border: round $warning 60%;
                }
                &.-active {
                    color: $text-warning 40%;
                    border: round $warning 40%;
                }
                &:disabled {
                    color: $text-warning 40%;
                    border: round $warning 40%;
                }
            }
    
            &.-error {
                color: $text-error;
                border: round $error;
                background: transparent;
                
                &:hover {
                    color: $text-error 60%;
                    border: round $error 60%;
                }
                &.-active {
                    color: $text-error 40%;
                    border: round $error 40%;
                }
                &:disabled {
                    color: $text-error 40%;
                    border: round $error 40%;
                }
            }
        }
    }
    """
