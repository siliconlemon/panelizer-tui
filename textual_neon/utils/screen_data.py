from typing import NamedTuple, Callable, Any, List, Set, Tuple, Coroutine


class ScreenData(NamedTuple):
    """
    A named tuple defining the data passed between screens.
    Stores the source screen's name, the payload, optional names for the items in the payload and
    a function to process the payload to aggregate iterative results for the next screen (if applicable).
    """
    source: str
    payload: List[Any] | Set[Any] | Tuple[Any] | None
    payload_names: list[str] | None = None
    function: Callable[[Any], bool | Coroutine] | None = None