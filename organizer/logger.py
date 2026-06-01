import logging
from pathlib import Path


def setup_logger(log_file: str = "logs/organizer.log"):
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("organizer")
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)

    handler = logging.FileHandler(log_path)
    fmt = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
    handler.setFormatter(fmt)
    logger.addHandler(handler)

    # also log to console
    ch = logging.StreamHandler()
    ch.setFormatter(fmt)
    logger.addHandler(ch)

    return logger
