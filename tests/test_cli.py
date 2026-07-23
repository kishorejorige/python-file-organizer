import pytest

from organizer.cli import main, build_parser


def test_cli_imports_without_watchdog_installed():
    from organizer import cli

    assert callable(cli.main)


def test_parser_accepts_config_overrides():
    args = build_parser().parse_args(
        [
            "downloads",
            "--config",
            "custom.json",
            "--dry-run",
            "--watch",
            "--no-recursive",
            "--rules-file",
            "rules.json",
            "--ignore-dir",
            "tmp",
            "--ignore-dir",
            "cache",
            "--verbose",
        ]
    )

    assert args.path == "downloads"
    assert args.config == "custom.json"
    assert args.dry_run is True
    assert args.watch is True
    assert args.recursive is False
    assert args.rules_file == "rules.json"
    assert args.ignore_dirs == ["tmp", "cache"]
    assert args.verbose is True


def test_main_reports_invalid_config(tmp_path):
    config_file = tmp_path / "config.json"
    config_file.write_text("{bad json", encoding="utf-8")

    try:
        main([str(tmp_path), "--config", str(config_file)])
    except SystemExit as exc:
        assert exc.code == 2
    else:
        raise AssertionError("invalid config should stop the CLI")


def test_main_missing_root_path(tmp_path):
    non_existent = tmp_path / "non_existent_folder"
    with pytest.raises(SystemExit) as excinfo:
        main([str(non_existent)])
    assert excinfo.value.code == 1


def test_main_root_path_is_file(tmp_path):
    file_path = tmp_path / "regular_file.txt"
    file_path.write_text("hello")
    with pytest.raises(SystemExit) as excinfo:
        main([str(file_path)])
    assert excinfo.value.code == 1


def test_main_missing_rules_file(tmp_path):
    config_file = tmp_path / "config.json"
    config_file.write_text('{"rules_file": "missing_rules.json"}', encoding="utf-8")

    # Passing the valid path as target workspace
    with pytest.raises(SystemExit) as excinfo:
        main([str(tmp_path), "--config", str(config_file)])
    assert excinfo.value.code == 1


def test_main_successful_dry_run(tmp_path):
    # Prepare directory
    src = tmp_path / "src"
    src.mkdir()
    (src / "file.txt").write_text("hello")

    config_file = tmp_path / "config.json"
    config_file.write_text('{"dry_run": true}', encoding="utf-8")

    # Run main, should succeed and return exit code 0 or raise SystemExit(0)
    result = main([str(src), "--config", str(config_file)])
    assert result == 0
    assert (src / "file.txt").exists()  # Dry run, file should not move
