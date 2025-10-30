import functools
import inspect
import json
from pathlib import Path
from typing import Any, Dict, Callable

from textual.app import App

from textual_neon.utils.paths import Paths


class Settings:
    """
    Manages settings and default fallbacks using a registry pattern.

    - The 'registry' holds the original, hardcoded 'factory' defaults using 'register_default'.
    - 'Settings' holds the user's saved settings, which are loaded from and saved
      to a JSON config file using 'load', 'set' and 'save'.
    - 'Get' operations prioritize settings before falling back to the registry.
    """
    DEFAULT_PREFS_DIR = Paths.app_base_dir() / "settings"

    @staticmethod
    def ensure(*, app: "App") -> "Settings":
        """
        Ensures the app has a 'settings' attribute.
        Use this in your screens to avoid linter warnings and other odd stuff.

        Usage:
        ::
            # In your Screen's __init__
            self.settings = Settings.ensure(app=self.app)
            s = self.settings
            self.some_setting: int = p.get("some_setting")
            ...
            # The rest of the screen's methods
            s = self.settings
            s.set("some_setting", new_value)
            ...
            # A setting watcher example
            def watch_theme(self, old_theme: str, new_theme: str) -> None:
                if new_theme in self.available_themes:
                    if hasattr(self, "settings") and not new_theme == self.settings.get("theme"):
                        self.settings.set("theme", new_theme)
                        self.settings.save()
                else:
                    self.theme = old_theme
            ...
            def watch_theme(self, old_theme: str, new_theme: str) -> None:
                if new_theme in self.available_themes:
                    if hasattr(self, "settings"):
                        self.settings.set("theme", new_theme)
                        self.settings.save()
                else:
                    self.theme = old_theme
        """
        if hasattr(app, "settings"):
            if not isinstance(app.settings, Settings):
                raise AttributeError(
                    f"App must have the 'settings' attribute set to an instance of 'Settings'. "
                    f"Different type detected: {type(app.settings)}"
                )
            else:
                return app.settings
        app.settings = Settings(config_dir=Settings.DEFAULT_PREFS_DIR)
        return app.settings

    def __init__(self, config_dir: Path = DEFAULT_PREFS_DIR, config_file: str = "settings.json"):
        self.config_file: Path = config_dir / config_file
        self._registry: Dict[str, Any] = {}
        self._user_prefs: Dict[str, Any] = {}

    def register_default(self, key: str, value: Any) -> None:
        """Registers a hardcoded 'factory default' value."""
        caller_self = None
        caller_name = "[unknown context]"
        stack = inspect.stack()

        if stack and len(stack) > 1:
            caller_frame = stack[1].frame
            if caller_frame and hasattr(caller_frame, 'f_locals'):
                caller_self = caller_frame.f_locals.get('self')
                if hasattr(caller_frame.f_code, 'co_name'):
                    caller_name = caller_frame.f_code.co_name

        if caller_self is None or not isinstance(caller_self, App):
            print(
                f"[Warning] Settings.register_default(key='{key}') was called from a non-App context "
                f"(from function '{caller_name}').\n"
                f"Factory defaults should be registered in your App's __init__ or a method "
                f"called by it to ensure a single source of truth.\n"
                f"{UserWarning}"
            )
        self._registry[key] = value

    def unregister_default(self, key: str) -> None:
        """
        Removes a 'factory default' from the registry.
        Also removes any corresponding settings to prevent orphans.
        """
        self._registry.pop(key, None)
        self._user_prefs.pop(key, None)

    def get(self, key: str) -> Any:
        """
        Gets the current value for a setting.
        Prioritizes the user's saved default, then the factory default.

        Raises:
            KeyError: If the key is not in the settings *or* the registry.
        """
        if key in self._user_prefs:
            return self._user_prefs[key]
        if key in self._registry:
            return self._registry[key]
        raise KeyError(f"No factory setting or user default '{key}' has been registered.")

    def set(self, key: str, value: Any) -> None:
        """
        Sets a user setting in memory.
        This does NOT save it to the file until 'save()' is called.
        """
        self._user_prefs[key] = value

    def get_all(self) -> Dict[str, Any]:
        """Returns a dictionary of all current settings, merging factory defaults with user settings."""
        current_settings = self._registry.copy()
        current_settings.update(self._user_prefs)

        return current_settings

    def load(self) -> None:
        """
        Loads user settings from the config file into memory.
        If the file doesn't exist or is corrupt, settings will be empty.
        """
        if self.config_file.exists():
            try:
                with self.config_file.open("r") as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        self._user_prefs = data
                    else:
                        self._user_prefs = {}
            except (IOError, json.JSONDecodeError):
                self._user_prefs = {}
        else:
            self._user_prefs = {}

    def save(self) -> None:
        """Saves the current user settings from memory to the config file."""
        try:
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            with self.config_file.open("w") as f:
                json.dump(self._user_prefs, f, indent=2, sort_keys=True)
        except IOError as e:
            print(f"[Settings] Error saving config file: {e}")

    def reset(self, key: str) -> None:
        """
        Resets a single user setting back to its factory value by removing it from
        the user's settings. Does not persist until saved.
        """
        self._user_prefs.pop(key, None)

    def reset_all(self) -> None:
        """
        Resets ALL user settings back to factory defaults by clearing
        the user setting map. Does not persist until saved.
        """
        self._user_prefs.clear()

    def save_result(self, key: str) -> Callable:
        """
        Decorator factory. When the decorated function (sync or async)
        finishes successfully, it saves the *return value* of the function
        to the specified 'key' and persists it to the 'settings' file.

        Usage (assuming self.app.settings is your Settings instance):
        ::
            @self.app.settings.save_result("user.name")
            async def get_user_name_from_dialog(self) -> str:
                #... logic to show a dialog ...
                return "The User's Name"

            # After this runs, settings will contain {"user.name": "The User's Name"}
        """
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                return_value = await func(*args, **kwargs)
                self.set(key, return_value)
                self.save()
                return return_value

            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs):
                return_value = func(*args, **kwargs)
                self.set(key, return_value)
                self.save()
                return return_value

            if inspect.iscoroutinefunction(func):
                return async_wrapper
            else:
                return sync_wrapper

        return decorator