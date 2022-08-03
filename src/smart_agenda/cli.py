#!/usr/bin/env python3
"""Command Line Interface for RF Switch Matrix client based on `click`.

.. program-output:: rfsc --help

"""

from pathlib import Path

import click
from rich.console import Console
from rich.table import Table

console = Console()


from smart_agenda import __version__
from smart_agenda.lib import read_agenda


def cb_version(ctx, param, value):
    if value:
        click.echo(__version__)
        exit(0)


@click.group(invoke_without_command=True)
@click.help_option("-h", "--help")
@click.option("-v", "--verbose", count=True, default=0, help="Increase verbosity of output.")
@click.option("--version", help="Print version number and exit.", is_flag=True, callback=cb_version, expose_value=False)
@click.argument("file", type=click.Path(exists=True, dir_okay=False, path_type=Path), required=False)
@click.pass_context
def cli(ctx, verbose, file):
    """Smart Agenda."""
    agenda = read_agenda(file)
    table = Table()
    table.add_column("Agenda")
    table.add_column("Time", justify="right", no_wrap=True)
    for item in agenda.items:
        table.add_row(item.name, item.duration)
    console.print(table)
