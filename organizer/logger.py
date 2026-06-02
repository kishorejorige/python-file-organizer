import logging
from pathlib import Path
from logging.handlers import RotatingFileHandler


def setup_logger(log_file: str = "logs/organizer.log"):
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("organizer")
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)

    # Rotating file handler to avoid unbounded growth
    fh = RotatingFileHandler(str(log_path), maxBytes=10 * 1024 * 1024, backupCount=5, encoding="utf-8")
    fmt = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s", datefmt="%Y-%m-%dT%H:%M:%S%z")
    fh.setFormatter(fmt)
    logger.addHandler(fh)

    # console handler
    ch = logging.StreamHandler()
    ch.setFormatter(fmt)
    logger.addHandler(ch)

    return logger
