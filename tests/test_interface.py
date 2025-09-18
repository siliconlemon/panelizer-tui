from pathlib import Path
from textual_fspicker import SelectDirectory


def test_pick_directory_valid(monkeypatch, tmp_path):
    """Simulate user input for directory picker."""
    test_input = str(tmp_path)

    monkeypatch.setattr("builtins.input", lambda: test_input)
    start_directory = Path.home() / "Pictures"
    result = SelectDirectory(location=start_directory, double_click_directories=False)

    assert result == test_input