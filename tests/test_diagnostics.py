import importlib.metadata
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from organizer.cli import main
from organizer.diagnostics import get_version, run_doctor


def test_get_version_success():
    with patch("importlib.metadata.version", return_value="1.6.0"):
        assert get_version() == "1.6.0"


def test_get_version_fallback():
    with patch(
        "importlib.metadata.version",
        side_effect=importlib.metadata.PackageNotFoundError,
    ):
        assert get_version() == "1.6.0"


def test_doctor_healthy(tmp_path):
    log_file = tmp_path / "doctor_healthy.log"
    # Run doctor under normal circumstances, should return 0 (healthy or warnings)
    exit_code = run_doctor(str(log_file))
    assert exit_code == 0
    assert log_file.exists()


def test_doctor_critical_failure_rules():
    with patch(
        "organizer.engine.rules.load_default_rules",
        side_effect=RuntimeError("Load error"),
    ):
        exit_code = run_doctor(None)
        assert exit_code == 1


def test_doctor_critical_failure_write_permission():
    with patch("tempfile.TemporaryDirectory", side_effect=OSError("Permission denied")):
        exit_code = run_doctor(None)
        assert exit_code == 1


def test_doctor_log_destination_failure(tmp_path):
    # Pass an invalid/unwritable log destination. A directory path cannot be opened for writing in append mode,
    # which is cross-platform and guaranteed to fail on both Windows and Unix.
    invalid_log = str(tmp_path)
    exit_code = run_doctor(invalid_log)
    assert exit_code == 1


def test_doctor_warnings_missing_watchdog():
    # Force watchdog import failure to test warning path
    with patch("watchdog.observers.Observer", None):
        exit_code = run_doctor(None)
        assert exit_code == 0


def test_doctor_warnings_missing_metadata():
    with patch(
        "importlib.metadata.metadata",
        side_effect=importlib.metadata.PackageNotFoundError,
    ):
        exit_code = run_doctor(None)
        assert exit_code == 0


def test_cli_version_flag():
    # CLI version flag exits with 0 and prints version
    with pytest.raises(SystemExit) as excinfo:
        main(["--version"])
    assert excinfo.value.code == 0


def test_cli_doctor_routing():
    with patch("organizer.cli.run_doctor", return_value=0) as mock_doctor:
        with pytest.raises(SystemExit) as excinfo:
            main(["doctor"])
        assert excinfo.value.code == 0
        mock_doctor.assert_called_once()


def test_cli_missing_path_fails():
    with pytest.raises(SystemExit) as excinfo:
        main([])
    assert excinfo.value.code == 2


def test_cli_backward_compatibility(tmp_path):
    target = tmp_path / "target_dir"
    target.mkdir()

    with patch("organizer.cli.setup_logger") as mock_logger_setup:
        mock_logger = MagicMock()
        mock_logger_setup.return_value = mock_logger

        with patch(
            "organizer.engine.organizer.OrganizerEngine.run", return_value=0
        ) as mock_run:
            result = main([str(target), "--dry-run"])
            assert result == 0
            mock_run.assert_called_once_with(Path(target), dry_run=True)
