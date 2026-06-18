"""Simple structured logger for the project."""

import logging


def get_logger(name: str):
    logger = logging.getLogger(name)

    if not logger.handlers:
        handler = logging.StreamHandler()

        formatter = logging.Formatter(
            "[%(asctime)s] [%(levelme)s] %(name)s: %(message)s"
        )

        handler.setFormatter(formatter)
        logger.addHandler(handler)

    logger.setLevel(logging.INFO)
    return logger


def log(message: str):
    """Simple print-style fallback logger"""
    print(f"[LOG] {message}")