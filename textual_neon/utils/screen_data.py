from typing import NamedTuple, Callable, Any, List, Set, Tuple, Awaitable


class ScreenData(NamedTuple):
    # noinspection GrazieInspection
    """
        A named tuple defining the data passed between screens.
        Stores the source screen's name, the payload, optional names for the items in the payload and
        a function to process the payload to aggregate iterative results for the next screen (if applicable).

        Usage:
        ::
            In your NeonApp descendant's __init__:
            self.state_machine.register(
                "home",
                screen_class=HomeScreen,
                next_state="loading",
                fallback=None,
                validate=lambda result: bool(result),
                data_from_result=lambda result:
                    ScreenData(
                        source="home",
                        payload=result,
                        payload_names=list(map(lambda path: path.split("/")[-1], result)),
                        function=lambda file_path: True,
                    ),
            )
        """
    source: str
    payload: List[Any] | Set[Any] | Tuple[Any, ...] | None
    payload_names: list[str] | None = None
    function: Callable[[Any], bool | Awaitable[bool]] | None = None