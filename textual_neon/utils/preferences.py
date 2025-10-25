import functools
import inspect
import json
from pathlib import Path
from typing import Any, Dict, Callable

from textual.app import App

from textual_neon.utils.paths import Paths


class Preferences:
    """
    Manages preferences and default fallbacks using a registry pattern.

    - The 'registry' holds the original, hardcoded 'factory' defaults.
    - 'Preferences' holds the user's saved preferences, which are loaded from and saved to a JSON config file.
    - 'Get' operations prioritize preferences before falling back to the registry.
    """
    DEFAULT_PREFS_DIR = Paths.app_base_dir() / "preferences"

    @staticmethod
    def ensure(*, app: "App") -> "Preferences":
        """
        Ensures the app has a 'preferences' attribute.
        Use this in your screens to avoid linter warnings and other odd stuff.

        Usage:
        ::
            # In your Screen's __init__
            self.preferences = Preferences.ensure(app=self.app)
            p = self.preferences
            self.some_preference: int = p.get("some_preference")

            # The rest of the screen's methods
            p = self.preferences
            p.set("some_preference", new_value)
        """
        if hasattr(app, "preferences"):
            if not isinstance(app.preferences, Preferences):
                raise AttributeError(
                    f"App must have the 'preferences' attribute set to an instance of 'Preferences'. "
                    f"Different type detected: {type(app.preferences)}"
                )
            else:
                return app.preferences
        app.preferences = Preferences(config_dir=Preferences.DEFAULT_PREFS_DIR)
        return app.preferences

    def __init__(self, config_dir: Path = DEFAULT_PREFS_DIR, config_file: str = "preferences.json"):
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
                f"[Warning] Preferences.register_default(key='{key}') was called from a non-App context "
                f"(from function '{caller_name}').\n"
                f"Factory defaults should be registered in your App's __init__ or a method "
                f"called by it to ensure a single source of truth.\n"
                f"{UserWarning}"
            )
        self._registry[key] = value

    def unregister_default(self, key: str) -> None:
        """
        Removes a 'factory default' from the registry.
        Also removes any corresponding preferences to prevent orphans.
        """
        self._registry.pop(key, None)
        self._user_prefs.pop(key, None)

    def get(self, key: str) -> Any:
        """
        Gets the current value for a setting.
        Prioritizes the user's saved default, then the factory default.

        Raises:
            KeyError: If the key is not in the preferences *or* the registry.
        """
        if key in self._user_prefs:
            return self._user_prefs[key]
        if key in self._registry:
            return self._registry[key]
        raise KeyError(f"No factory setting or user default '{key}' has been registered.")

    def set(self, key: str, value: Any) -> None:
        """
        Sets a user preference in memory.
        This does NOT save it to the file until 'save()' is called.
        """
        self._user_prefs[key] = value

    def get_all(self) -> Dict[str, Any]:
        """Returns a dictionary of all current settings, merging factory defaults with user preferences."""
        current_settings = self._registry.copy()
        current_settings.update(self._user_prefs)

        return current_settings

    def load(self) -> None:
        """
        Loads user preferences from the config file into memory.
        If the file doesn't exist or is corrupt, preferences will be empty.
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
        """Saves the current user preferences from memory to the config file."""
        try:
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            with self.config_file.open("w") as f:
                json.dump(self._user_prefs, f, indent=2, sort_keys=True)
        except IOError as e:
            print(f"[Preferences] Error saving config file: {e}")

    def reset(self, key: str) -> None:
        """
        Resets a single user preference back to its factory value by removing it from
        the user's preferences. Does not persist until saved.
        """
        self._user_prefs.pop(key, None)

    def reset_all(self) -> None:
        """
        Resets ALL user preferences back to factory defaults by clearing
        the user preference map. Does not persist until saved.
        """
        self._user_prefs.clear()

    def set_preference(self, key: str, value: Any) -> Callable:
        """
        Decorator factory. When the decorated function (sync or async)
        finishes successfully, it sets the provided key/value and
        saves it to the 'preferences' file.

        Usage (assuming self.app.preferences is your Preferences instance):
        ::
            @self.app.preferences.set_preference("user.name", "Default User")
            async def on_button_pressed(self, ...):
                # button logic ...
        """
        def decorator(func: Callable) -> Callable:
            if inspect.iscoroutinefunction(func):
                @functools.wraps(func)
                async def async_wrapper(*args, **kwargs):
                    return_value = await func(*args, **kwargs)
                    print(f"[Preferences] Async func {func.__name__} finished. "
                          f"Setting '{key}' to '{value}' and saving.")
                    self.set(key, value)
                    self.save()
                    return return_value
                return async_wrapper
            else:
                @functools.wraps(func)
                def sync_wrapper(*args, **kwargs):
                    return_value = func(*args, **kwargs)
                    print(f"[Preferences] Sync func {func.__name__} finished. Setting '{key}' to '{value}' and saving.")
                    self.set(key, value)
                    self.save()
                    return return_value
                return sync_wrapper

        return decorator