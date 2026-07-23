import pytest

from organizer.config import ConfigError, FILE_TYPES, load_config, DEFAULT_CONFIG
from organizer.engine.rules import validate_rules


def test_file_types_exist():
    assert "Images" in FILE_TYPES
    assert "Documents" in FILE_TYPES
    assert "Audio" in FILE_TYPES


def test_invalid_config_warns_and_uses_defaults(tmp_path):
    config_file = tmp_path / "config.json"
    config_file.write_text("{bad json", encoding="utf-8")

    with pytest.warns(RuntimeWarning, match="Could not load config file"):
        cfg = load_config(str(config_file))

    assert cfg["recursive"] is True


def test_invalid_config_strict_raises(tmp_path):
    config_file = tmp_path / "config.json"
    config_file.write_text("{bad json", encoding="utf-8")

    with pytest.raises(ConfigError, match="Could not load config file"):
        load_config(str(config_file), strict=True)


def test_missing_config_strict_raises(tmp_path):
    config_file = tmp_path / "non_existent_config.json"
    with pytest.raises(FileNotFoundError, match="Config file not found"):
        load_config(str(config_file), strict=True)


def test_missing_config_not_strict_uses_default():
    cfg = load_config("non_existent_config.json", strict=False)
    assert cfg["dry_run"] == DEFAULT_CONFIG["dry_run"]
    assert cfg["recursive"] == DEFAULT_CONFIG["recursive"]


def test_valid_config_values(tmp_path):
    config_file = tmp_path / "config.json"
    config_file.write_text(
        '{"dry_run": true, "ignore_dirs": ["cache"]}', encoding="utf-8"
    )
    cfg = load_config(str(config_file), strict=True)
    assert cfg["dry_run"] is True
    assert "cache" in cfg["ignore_dirs"]


def test_invalid_config_types_strict(tmp_path):
    config_file = tmp_path / "config.json"
    config_file.write_text('{"dry_run": "not_a_bool"}', encoding="utf-8")
    with pytest.raises(ConfigError, match="Config key 'dry_run' must be of type bool"):
        load_config(str(config_file), strict=True)


def test_invalid_ignore_dirs_type(tmp_path):
    config_file = tmp_path / "config.json"
    config_file.write_text('{"ignore_dirs": [123, "valid"]}', encoding="utf-8")
    with pytest.raises(ConfigError, match="All items in ignore_dirs must be strings"):
        load_config(str(config_file), strict=True)


def test_rules_validation_success():
    valid_rules = [
        {"folder": "Photos", "extensions": [".jpg", ".png"]},
        {"folder": "Texts", "extensions": [".txt"]},
    ]
    # Should run without error
    validate_rules(valid_rules)


def test_rules_validation_invalid_structure():
    with pytest.raises(ValueError, match="Rules must be a list"):
        validate_rules("not a list")

    with pytest.raises(ValueError, match="must be a dictionary"):
        validate_rules(["not a dict"])

    with pytest.raises(ValueError, match="missing required key 'folder'"):
        validate_rules([{"extensions": [".txt"]}])

    with pytest.raises(ValueError, match="missing required key 'extensions'"):
        validate_rules([{"folder": "Texts"}])


def test_rules_validation_invalid_types():
    with pytest.raises(ValueError, match="'folder' must be a non-empty string"):
        validate_rules([{"folder": 123, "extensions": [".txt"]}])

    with pytest.raises(ValueError, match="'extensions' must be a list of strings"):
        validate_rules([{"folder": "Texts", "extensions": [123]}])

    with pytest.raises(ValueError, match="must be a string starting with a '.'"):
        validate_rules([{"folder": "Texts", "extensions": ["txt"]}])


def test_rules_validation_path_traversal():
    with pytest.raises(ValueError, match="path traversal elements"):
        validate_rules([{"folder": "../unsafe", "extensions": [".txt"]}])

    with pytest.raises(ValueError, match="path traversal elements"):
        validate_rules([{"folder": "unsafe/sub", "extensions": [".txt"]}])

    with pytest.raises(ValueError, match="path traversal elements"):
        validate_rules([{"folder": "unsafe\\sub", "extensions": [".txt"]}])
