from typing import List, Literal

from textual.app import ComposeResult
from textual.widget import Widget
from ..widgets import SimpleInput

class SimpleInputGrid(Widget):
    """
    A generic NxM grid widget with labels and units.
    Each cell is defined by one entry in the parallel lists (values, labels, units, types).
    """
    DEFAULT_CSS = """
    SimpleInputGrid {
        width: 100%;
        height: auto;
        layout: grid;
        
        .grid-cell {
            margin: 0;
            padding-right: 2;
        }
        
    }
    """

    def __init__(
            self,
            *,
            rows: int,
            columns: int,
            values: List[int],
            labels: List[str],
            input_ids: List[str],
            units: List[str | None] | None = None,
            types: Literal["integer", "number", "text"] | None = None,
            **kwargs
    ):
        super().__init__(**kwargs)
        self.rows = rows
        self.columns = columns
        n_expected = rows * columns
        n_values = len(values)
        n_labels = len(labels)
        n_input_ids = len(input_ids)
        if not (n_values == n_labels == n_input_ids):
            raise ValueError(
                f"SimpleInputGrid: Mismatched argument lengths: "
                f"values={n_values}, labels={n_labels}, "
                f"input_ids={n_input_ids}"
            )
        if n_values != n_expected:
            raise ValueError(
                f"SimpleInputGrid: Given rows={rows} columns={columns} → {n_expected} cells, "
                f"but got {n_values} values (and similarly for other fields)."
            )
        self.values = values
        self.labels = labels
        self.input_ids = input_ids
        self.units = units if units else [None] * n_expected
        self.types = types if types else ["integer"] * n_expected

    async def on_mount(self):
        self.styles.height = self.rows * 4
        self.styles.grid_size_rows = self.rows
        self.styles.grid_size_columns = self.columns
        self.styles.grid_columns = ["1fr"] * self.columns
        self.styles.grid_rows = [4] * self.rows

    def compose(self) -> ComposeResult:
        n_cells = self.rows * self.columns
        for idx in range(n_cells):
            yield SimpleInput(
                label=self.labels[idx],
                value=self.values[idx],
                input_id=self.input_ids[idx],
                unit=self.units[idx],
                type_=self.types[idx],
                classes="grid-cell"
            )