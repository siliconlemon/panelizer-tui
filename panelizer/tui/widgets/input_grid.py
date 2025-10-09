from textual.app import ComposeResult
from textual.containers import Vertical, Horizontal
from textual.widget import Widget
from textual.widgets import Static, Input


class InputGrid(Widget):
    """
    A generic NxM grid widget with labels, suffixes and custom units.
    Each cell is defined by one entry in the parallel lists (values, labels, suffixes and units).
    """
    DEFAULT_CSS = """
    InputGrid {
        width: 100%;
        height: auto;
        margin-bottom: 1;
        layout: grid;

        .grid-cell {
            margin: 0;
            padding-right: 2;
        }
        .grid-row {
            layout: horizontal;
            align-vertical: middle;
            height: auto;
            width: 1fr;
            margin-bottom: 0;
            padding: 0;
        }
        .input {
            color: $text;
            width: 1fr;
            min-width: 10;
            min-height: 1;
            padding: 0 1;
            margin: 0;
        }
        .unit {
            color: $text-muted;
            width: 2;
            margin: 1 0 0 1;
        }
    }
    """

    def __init__(
            self,
            *,
            rows: int,
            columns: int,
            values: list[int],
            labels: list[str],
            input_ids: list[str],
            units: list[str] = None,
            **kwargs
    ):
        super().__init__(**kwargs)
        self.rows = rows
        self.columns = columns
        self.ROW_HEIGHT = 4
        self.COLUMN_WIDTH = "1fr"
        n_expected = rows * columns
        n_values = len(values)
        n_labels = len(labels)
        n_input_ids = len(input_ids)
        if not (n_values == n_labels == n_input_ids):
            raise ValueError(
                f"GridInput: Mismatched argument lengths: "
                f"values={n_values}, labels={n_labels}, "
                f"input_ids={n_input_ids}"
            )
        if n_values != n_expected:
            raise ValueError(
                f"GridInput: Given rows={rows} columns={columns} → {n_expected} cells, "
                f"but got {n_values} values (and similarly for other fields)."
            )
        self.values = values
        self.labels = labels
        self.input_ids = input_ids
        self.units = units if units else [None] * n_expected

    async def on_mount(self):
        self.styles.height = self.rows * self.ROW_HEIGHT
        self.styles.grid_size_rows = self.rows
        self.styles.grid_size_columns = self.columns
        self.styles.grid_columns = [self.COLUMN_WIDTH] * self.columns
        self.styles.grid_rows = [self.ROW_HEIGHT] * self.rows

    def compose(self) -> ComposeResult:
        n_cells = self.rows * self.columns
        for idx in range(n_cells):
            label = self.labels[idx]
            element_id = self.input_ids[idx]
            value = self.values[idx]
            unit = self.units[idx]
            with Vertical(classes="grid-cell"):
                yield Static(label, classes="input-label")
                with Horizontal(classes="grid-row"):
                    yield Input(str(value), id=element_id, classes="input", type="number")
                    if unit:
                        yield Static(unit, classes="unit", disabled=True)