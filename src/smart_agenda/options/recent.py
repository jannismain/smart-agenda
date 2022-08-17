import click

from smart_agenda.cli import app_dir


def recent(func=None, **options):
    """Provide ``-q/--quiet`` option."""

    def inner(f):
        return click.option(
            "--recent",
            help="Load recently saved agenda.",
            type=click.Path(),
            shell_complete=comp_recent_agendas,
            callback=cb_recent,
            **options,
        )(f)

    return inner(func) if func else inner


def cb_recent(ctx, param, filename):
    if filename:
        fp = app_dir / filename
        if not fp.exists():
            raise click.BadParameter(f"'{filename}' not found in '{app_dir}'")
        return fp


def comp_recent_agendas(ctx, args, incomplete):  # noqa
    return sorted(fp.name for fp in app_dir.glob("*") if not incomplete or fp.name.startswith(incomplete))
