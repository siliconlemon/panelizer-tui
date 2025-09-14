from panelizer.tui import pick_directory


def test_pick_directory_valid(monkeypatch, tmp_path):
    """Simulate user input for directory picker."""
    test_input = str(tmp_path)

    monkeypatch.setattr("builtins.input", lambda: test_input)
    result = pick_directory("Select test directory")

    assert result == test_input
