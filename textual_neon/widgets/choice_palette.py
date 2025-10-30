from textual import on
from typing import Literal, Any
from textual.widget import Widget
from collections.abc import Callable
from textual.containers import Horizontal, Vertical, Container
from textual_neon.widgets.choice_button import ChoiceButton

class ChoicePalette(Widget, inherit_css=True):
    """
    A palette widget for setting up multiple choices with ChoiceButton entries.
    Can be either horizontal or vertical.

    Usage:
    ::
        @on(ChoiceButton.Selected)
        async def file_mode_changed(self):
            palette = self.query_one("#file-mode-palette", ChoicePalette)
            idx = palette.selected_idx
            if idx == 0:
                self.file_mode = "all"
                self.selected_files = []
            elif idx == 1:
                self.file_mode = "select"
                files = await self.app.push_screen_wait(ListSelectDialog(items))
                self.selected_files = files or []
    """
    DEFAULT_CSS = """
    ChoicePalette {
        height: auto;
        width: 100%;
        Horizontal, Vertical {
            border: round $foreground 60%;
            border-title-color: $foreground 70%;
            height: auto;
        }
    }
    """

    def __init__(
        self,
        *,
        name: str,
        labels: list[str],
        actions: list[Callable | None],
        default_idx: int | None = None,
        labels_when_selected: list[str | Callable[[], str]] | None = None,
        orientation: Literal["horizontal", "vertical"] = "horizontal",
        **kwargs
    ) -> None:
        super().__init__(name=name, **kwargs)
        self.orientation = orientation
        self.labels = labels
        self.actions = actions or [None] * len(labels)
        self.labels_when_selected = labels_when_selected or [None] * len(labels)
        self._buttons = []
        self._default_idx = default_idx

    def compose(self):
        self._buttons.clear()
        container = Horizontal if self.orientation == "horizontal" else Vertical
        num = len(self.labels)
        with container():
            for idx, label in enumerate(self.labels):
                btn = ChoiceButton(
                    label=label,
                    action=self.actions[idx] if idx < len(self.actions) else None,
                    label_when_selected=self.labels_when_selected[idx]
                        if idx < len(self.labels_when_selected) else None,
                )
                if self.orientation == "horizontal":
                    if idx < num - 1:
                        btn.styles.margin = (0, 2, 0, 1)
                    else:
                        btn.styles.margin = (0, 1, 0, 2)
                elif self.orientation == "vertical" and idx < num - 1:
                        btn.styles.margin = (0, 0, 1, 0)
                self._buttons.append(btn)
                yield btn

    async def on_mount(self) -> None:
        if self.orientation == "horizontal":
            self.query_one(Horizontal).border_title = self.name
        elif self.orientation == "vertical":
            self.query_one(Vertical).border_title = self.name
        idx = self._default_idx
        if (
            idx is not None
            and 0 <= idx < len(self._buttons)
        ):
            for i, btn in enumerate(self._buttons):
                btn.set_selected(i == idx)

    def refresh_disp_state(self) -> None:
        """
        Refreshes the display state and labels of all buttons based on the current state.
        Useful if any of the labels_when_selected is a lambda that uses the caller's state post-press.
        """
        self.select(self.selected_idx)

    def select(self, idx: int) -> None:
        """
        Selects the button at the given index. This alone refreshes the display state,
        no need to call refresh_disp_state after.
        """
        if 0 <= idx < len(self._buttons):
            for i, btn in enumerate(self._buttons):
                btn.set_selected(i == idx)

    @on(ChoiceButton.Selected)
    def handle_selection(self, event: ChoiceButton.Selected):
        try:
            chosen_idx = self.buttons.index(event.button)
        except ValueError:
            chosen_idx = -1
        for i, btn in enumerate(self.buttons):
            btn.set_selected(i == chosen_idx)

    @property
    def selected_idx(self) -> int:
        for idx, btn in enumerate(self.buttons):
            if btn.selected:
                return idx
        return -1

    @property
    def selected_button(self):
        idx = self.selected_idx
        return self.buttons[idx] if idx != -1 else None

    @property
    def buttons(self) -> tuple[ChoiceButton, ...]:
        return tuple(self._buttons)
