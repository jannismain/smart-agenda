from pathlib import Path
import logging as log
import re
from dataclasses import dataclass

import pick


@dataclass
class AgendaItem:
    name: str
    duration: int


@dataclass
class Agenda:
    title: str
    items: list[AgendaItem]


agenda_item_pattern = re.compile(r"[-\*] (.*) \((\d?\d\:\d\d)\)")


def read_agenda(filepath: Path = None, title: str = None) -> Agenda:
    if filepath is None:
        md_files = list(Path.cwd().glob("*.md"))
        log.debug(md_files)
        filepath, idx = pick.pick(md_files)

    with filepath.open() as fp:
        content = fp.read()

    if title is None:
        if content.splitlines()[0].startswith("#"):
            title = content.splitlines()[0][2:]
        else:
            title = "Meeting"

    agenda_items = [AgendaItem(*match) for match in agenda_item_pattern.findall(content)]

    return Agenda(title, agenda_items)
