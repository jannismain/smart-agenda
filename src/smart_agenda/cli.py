"""Smart Agenda CLI.

.. program-output:: smart-agenda --help
"""
from pathlib import Path

import click
from rich.console import Console
from rich.live import Live

console = Console()

app_dir = Path(click.get_app_dir(app_name="smart-agenda", force_posix=True))

from smart_agenda import __version__
from smart_agenda.cli_output import render_completed_agenda, render_initial_agenda, render_running_agenda
from smart_agenda.lib import Agenda
from smart_agenda.options import recent
from smart_agenda.util import get_filepath


def cb_version(ctx, param, value):
    """When `--version` is given, echo version and exit."""
    if value:
        click.echo(__version__)
        exit(0)


EXAMPLE_AGENDA = """
# Meeting Title

Check-In     5:00
First Topic 12:00
Second Topic 7:00
AOB          6:00
""".lstrip()


@click.group(invoke_without_command=True)
@click.help_option("-h", "--help")
@click.option("-v", "--verbose", count=True, default=0, help="Increase verbosity of output.")
@click.option("--version", help="Print version number and exit.", is_flag=True, callback=cb_version, expose_value=False)
@click.option("--example", help="Show example agenda.", is_flag=True)
@click.option("--skip-input", help="Skip manual agenda input.", is_flag=True)
@click.option("--demo", help="Shorthand for `--example --skip-input`.", is_flag=True)
@click.option("--edit", help="Edit agenda before starting the meeting.", is_flag=True)
@click.option("--title", help="Title of your agenda.")
@click.option("--save/--no-save", help="Save agenda for later.", default=True, show_default=True, is_flag=True)
@recent
@click.argument("file", type=click.File(), required=False)
@click.pass_context
def cli(ctx, verbose, example, save, recent, skip_input, demo, edit, title, file):
    """Smart Agenda."""
    # TODO: refactor content loading and title handling
    console.clear()
    if file:
        content = file.read()
        save = False
    elif recent:
        content = recent.open().read()
        if edit:
            content = prompt_for_agenda(template=content, title=title)
        else:
            save = False
    elif (example and skip_input) or demo:
        content = EXAMPLE_AGENDA
    else:
        content = prompt_for_agenda(template=EXAMPLE_AGENDA if example else "", title=title)

    if not content.strip():
        # click.secho("No text provided.", dim=True, italic=True)
        exit(0)
    agenda = Agenda.loads(content)
    if not len(agenda.items):
        click.secho(
            "No agenda items found.\nSee `--example` for the expected agenda format.",
            dim=True,
            fg="yellow",
            italic=True,
        )
        exit(0)

    if save:
        fp_agenda = get_filepath(agenda, parent=app_dir)
        fp_agenda.open("w").write(content)

    main(agenda)


def prompt_for_agenda(template: str = None, title: str = None) -> str:
    """Prompt user to enter agenda."""
    console.print("[d][i]Enter agenda in external editor. Close the file to continue...")
    if title:
        if template.startswith("#"):
            # remove template heading, as title is already provided
            template = "\n".join(template.split("\n")[1:]).lstrip()
        title_str = f"# {title}"
        template = f"{title_str}\n\n{template}"
    return click.edit(template, require_save=False) + "\n"


KEY_UP, KEY_DOWN, KEY_RIGHT, KEY_LEFT = [f"\x1b[{c}" for c in "ABCD"]
KEY_ENTER, KEY_BACKSPACE = ("\n", "\x7f")
KEYS_PREVIOUS = ("b", KEY_UP, KEY_LEFT, KEY_BACKSPACE)
KEYS_NEXT = ("n", KEY_DOWN, KEY_RIGHT, KEY_ENTER)


def main(agenda: Agenda):
    """Main loop to handle cli state."""
    console.clear()
    console.print(render_initial_agenda(agenda))
    console.input("Press enter to start...")
    console.clear()
    agenda.to_next()

    import getchlib

    with Live(render_running_agenda(agenda), auto_refresh=False, console=console) as live:
        agenda_completed = False
        while not agenda_completed:
            live.update(render_running_agenda(agenda), refresh=True)
            key = getchlib.getkey(False, 0.1)
            if key in KEYS_NEXT:
                agenda_completed = agenda.to_next()
            if key in KEYS_PREVIOUS:
                agenda.to_previous()

        live.update(render_completed_agenda(agenda))


if __name__ == "__main__":
    agenda = Agenda.loads(Path("test.md").open().read())
    main(agenda)
