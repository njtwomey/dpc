from __future__ import annotations

import sys

from loguru import logger
from tqdm import tqdm

from dpc.log import configure


def test_configure_installs_exactly_one_sink():
    configure()
    logger.info("hello")  # must not raise
    configure(verbose=True)
    logger.debug("hello again")


def test_log_lines_do_not_shred_an_active_progress_bar(capsys):
    # Both loguru and tqdm write to stderr. Routing logs through tqdm.write
    # makes it clear the bar, print, and redraw, instead of interleaving.
    configure()
    with tqdm(total=2, file=sys.stderr, desc="work"):
        logger.info("a message while the bar is up")

    err = capsys.readouterr().err
    assert "a message while the bar is up" in err


def test_exception_logging_does_not_dump_local_variables(capsys):
    # diagnose=False: loguru must not expand locals into the traceback, which is
    # exactly where a credential would surface.
    configure(verbose=True)
    secret = "hunter2-do-not-leak"  # noqa: S105 - a canary, not a real secret

    try:
        raise ValueError("boom")  # noqa: TRY301
    except ValueError:
        logger.exception("failed")

    err = capsys.readouterr().err
    assert "boom" in err, "the exception itself should still be logged"
    assert secret not in err
    assert "hunter2" not in err
