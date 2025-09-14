import os
from rich.prompt import Prompt
from rich.console import Console


console = Console()

def pick_directory(prompt_text: str = "Select directory") -> str | None:
    """
    Ask the user for an existing directory path with basic validation.

    Args:
        prompt_text (str): Message to display

    Returns:
        str: Validated directory path
    """
    while True:
        path = Prompt.ask(f"[bold cyan]{prompt_text}")
        if not path:
            console.print("[red]Error: Empty path. Try again.")
            continue

        path = os.path.abspath(path)
        if os.path.isdir(path):
            return path
        else:
            console.print(f"[red]'{path}' is not a valid directory. Try again.")
