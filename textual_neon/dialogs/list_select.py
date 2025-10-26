from textual_neon.dialogs.neon_dialog import NeonDialog


class ListSelectDialog(NeonDialog):
    """A dialog based on NeonDialog for selecting one or more items from a list.

    Usage:
    ::
        async def on_button_pressed(self, event: textual.widgets.Button.Pressed) -> None:
            match event.button.id:
                case "select-files-btn":
                    self.run_worker(self._select_files_worker, exclusive=True)
                    event.stop()
        ...
        async def _select_files_worker(self) -> None:
            files = await self.app.push_screen_wait(ListSelectDialog())
            self.selected_files = files or []
        ...
        async def on_unmount(self) -> None:
            self.workers.cancel_all()
    """
    pass