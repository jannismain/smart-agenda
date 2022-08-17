import hashlib
from pathlib import Path

from smart_agenda.lib import Agenda


def get_filepath(agenda: Agenda, parent: Path = None) -> Path:
    # create filename from agenda title
    filename = "-".join(agenda.title.split()) if agenda.title else "unnamed-agenda"

    if parent is not None:
        if not parent.exists():
            parent.mkdir(parents=True)
        filepath = parent / filename
    else:
        filepath = Path(filename)

    # add hash to prevent overwriting different agenda with same title
    # same agendas (based on title & items) will produce same hash to avoid saving duplicates
    if filepath.exists():
        hash_content = ";".join((agenda.title, *(";".join((item.name, str(item.duration))) for item in agenda.items)))
        agenda_hash = hashlib.md5(hash_content.encode()).hexdigest()
        filepath = filepath.with_name(f"{filename}_{agenda_hash[:8]}")

    return filepath
