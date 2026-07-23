import logging

from organizer.logger import setup_logger


def test_logger_setup_no_duplicates():
    # Setup logger multiple times
    setup_logger(None, level=logging.INFO)
    logger = setup_logger(None, level=logging.DEBUG)

    # Should only have one StreamHandler
    handlers = logger.handlers
    assert len(handlers) == 1
    assert isinstance(handlers[0], logging.StreamHandler)
    assert logger.level == logging.DEBUG


def test_logger_file_creation(tmp_path):
    log_file = tmp_path / "test_run.log"
    logger = setup_logger(str(log_file), level=logging.INFO)

    assert len(logger.handlers) == 2  # console + file

    # Log a message and check file content
    logger.info("Test log statement")

    # Flush and close handlers to release the file lock (important for Windows/WSL)
    for handler in logger.handlers:
        handler.flush()
        handler.close()

    assert log_file.exists()
    content = log_file.read_text(encoding="utf-8")
    assert "Test log statement" in content


def test_logger_invalid_file_fallback():
    # Attempting to log to a path that is not writeable (e.g. empty path or directory structure error)
    # The setup_logger function should fall back to console only and warn, without crashing.
    logger = setup_logger("", level=logging.INFO)
    assert len(logger.handlers) == 1  # Should fall back to console only
    assert isinstance(logger.handlers[0], logging.StreamHandler)
