"""Logging setup.

One loguru sink, configured once from the CLI. Library modules just
``from loguru import logger`` and log; they never add handlers of their own.
"""

from __future__ import annotations

import sys

from loguru import logger
from tqdm import tqdm

FORMAT = (
    "<green>{time:HH:mm:ss}</green> "
    "<level>{level: <8}</level> "
    "<cyan>{name}</cyan> - <level>{message}</level>"
)


def _write(message: str) -> None:
    """Emit through tqdm, so a log line does not shred an active progress bar.

    Both write to stderr; tqdm.write clears the bar, prints, and redraws it.
    With no bar on screen this is just a write to stderr.
    """
    tqdm.write(message, end="", file=sys.stderr)


def configure(*, verbose: bool = False) -> None:
    """Point loguru at stderr at the requested verbosity."""
    logger.remove()
    logger.add(
        _write,
        level="DEBUG" if verbose else "INFO",
        format=FORMAT,
        colorize=True,
        backtrace=verbose,
        diagnose=False,
        # diagnose=False keeps local variables out of tracebacks; credentials
        # pass through this code and must never reach a log line.
    )
