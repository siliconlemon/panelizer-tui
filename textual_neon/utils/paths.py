import platform
import sys
from pathlib import Path
from typing import Iterable


class Paths:
    """Cross-platform utility for getting standard user directories."""

    @staticmethod
    def _get_xdg_dir(xdg_var: str, fallback: str) -> Path:
        """Helper to read XDG user directories on Linux."""
        xdg_config = Path.home() / ".config" / "user-dirs.dirs"
        if xdg_config.exists():
            # noinspection PyBroadException
            try:
                with xdg_config.open("r") as f:
                    for line in f:
                        if line.startswith(xdg_var):
                            # Format: XDG_PICTURES_DIR="$HOME/Pictures"
                            path_str = line.split("=", 1)[1].strip().strip('"')
                            path_str = path_str.replace("$HOME", str(Path.home()))
                            return Path(path_str)
            except Exception:
                pass
        return Path.home() / fallback

    @staticmethod
    def app_base_dir() -> Path:
        """
        Finds the base directory for the application's data.

        - For packaged executables ('frozen'), this is the directory
          containing the executable.
        - For standard .py execution, this relies on the app being
          run from the project root (e.g., `python -m digger.app`).
        """
        if getattr(sys, 'frozen', False):
            return Path(sys.executable).parent.resolve()

        return Path.cwd().resolve()

    @staticmethod
    def all_files_in_dir(dir_path: Path, *, extensions: Iterable[str] = None) -> Iterable[Path]:
        """Yields all files in a directory, sorted by name, optionally filtering by extensions."""
        if not dir_path.is_dir():
            return

        allowed_suffixes = None
        if extensions:
            allowed_suffixes = {f".{ext.lower().lstrip('.')}" for ext in extensions}

        try:
            sorted_files = sorted(dir_path.iterdir())
        except OSError:
            return

        for file_path in sorted_files:
            if file_path.is_file():
                if allowed_suffixes:
                    if file_path.suffix.lower() in allowed_suffixes:
                        yield file_path
                else:
                    yield file_path

    @staticmethod
    def pictures() -> Path:
        """Returns the default Pictures directory for the current OS."""
        system = platform.system()

        if system == "Windows":
            return Path.home() / "Pictures"
        elif system == "Darwin":
            return Path.home() / "Pictures"
        elif system == "Linux":
            return Paths._get_xdg_dir("XDG_PICTURES_DIR", "Pictures")
        else:
            return Path.home() / "Pictures"

    @staticmethod
    def documents() -> Path:
        """Returns the default Documents directory for the current OS."""
        system = platform.system()

        if system == "Windows":
            return Path.home() / "Documents"
        elif system == "Darwin":
            return Path.home() / "Documents"
        elif system == "Linux":
            return Paths._get_xdg_dir("XDG_DOCUMENTS_DIR", "Documents")
        else:
            return Path.home() / "Documents"

    @staticmethod
    def downloads() -> Path:
        """Returns the default Downloads directory for the current OS."""
        system = platform.system()

        if system == "Windows":
            return Path.home() / "Downloads"
        elif system == "Darwin":
            return Path.home() / "Downloads"
        elif system == "Linux":
            return Paths._get_xdg_dir("XDG_DOWNLOAD_DIR", "Downloads")
        else:
            return Path.home() / "Downloads"

    @staticmethod
    def videos() -> Path:
        """Returns the default Videos directory for the current OS."""
        system = platform.system()

        if system == "Windows":
            return Path.home() / "Videos"
        elif system == "Darwin":
            return Path.home() / "Movies"  # macOS uses "Movies" instead
        elif system == "Linux":
            return Paths._get_xdg_dir("XDG_VIDEOS_DIR", "Videos")
        else:
            return Path.home() / "Videos"

    @staticmethod
    def music() -> Path:
        """Returns the default Music directory for the current OS."""
        system = platform.system()

        if system == "Windows":
            return Path.home() / "Music"
        elif system == "Darwin":
            return Path.home() / "Music"
        elif system == "Linux":
            return Paths._get_xdg_dir("XDG_MUSIC_DIR", "Music")
        else:
            return Path.home() / "Music"