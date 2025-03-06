import logging
import os
import sys


def setup_logger(name, log_file=None, level=logging.INFO):
    """Return a logger with the specified name and level.

    If a log file is specified, the logger will write to that file. Otherwise, it will write to
    stdout.

    Parameters
    ----------
    name : str
        The name of the logger.
    log_file : str, optional
        The path to the log file. If not specified, the logger will write to stdout.
    level : int, optional
        The logging level.

    Returns
    -------
    logging.Logger
        The logger.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    formatter = logging.Formatter("[%(name)s: %(levelname)s] - %(message)s")

    if log_file is not None:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        handler = logging.FileHandler(log_file)
    else:
        handler = logging.StreamHandler(sys.stdout)

    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger


LOGGER = setup_logger("random_kingdominion")
