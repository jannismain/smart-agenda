import logging
from contextlib import contextmanager
from typing import Callable

import pytest
from click.testing import CliRunner, Result

from smart_agenda.cli import cli as f_cli

env = {}


@pytest.fixture()
def cli() -> Callable:
    def invoke(*args, mix_stderr=False, **kwargs):
        runner: CliRunner = CliRunner(mix_stderr=mix_stderr)

        # click testing and logging output might produce issues with broken streams
        # (e.g. ValueError: I/O operation on closed file.)
        # see https://github.com/pallets/click/issues/824
        # Therefore, we disable any logging output during cli execution
        # with mute_logging():
        return runner.invoke(f_cli, *args, env=env, **kwargs)

    yield invoke


def test_main(cli):
    rv: Result = cli()
    logging.info(rv.stdout)
    assert rv.exit_code == 0


def test_script():
    import subprocess

    cmd = ["smart-agenda", "--help"]
    assert subprocess.check_call(cmd) == 0
    output = subprocess.check_output(cmd).decode()
    logging.info(output)
    assert output


def test_module_exec():
    import subprocess

    cmd = ["python", "-m", "smart_agenda", "--help"]
    assert subprocess.check_call(cmd) == 0
    output = subprocess.check_output(cmd).decode()
    logging.info(output)
    assert output


def test_cli_version(cli):
    rv: Result = cli(["--version"])
    assert rv.exit_code == 0


@contextmanager
def mute_logging(level: int = logging.CRITICAL):
    """Context manager that mutes logging.

    Args:
        level: upper level of log messages to mute (default: :py:attr:`logging.CRITICAL`).

    Example:

        Mute all log messages

        >>> logging.info("This will get logged")
        >>> with mute_logging():
        ...     logging.info("This won't get logged")

        Only mute log messages of level :py:attr:`logging.INFO`

        >>> logging.info("This will get logged")
        >>> with mute_logging(logging.INFO):
        ...     logging.info("This won't get logged")
        ...     logging.error("This, however, will be logged again")
    """
    logger_disabled = False
    if logging.getLogger().level <= level:
        logging.disable(level)
        logger_disabled = True
    yield
    if logger_disabled:
        # enable logger again by removing previous disable level
        logging.disable(logging.NOTSET)
