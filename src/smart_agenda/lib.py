# required to support <=Python3.9
from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path

import pick

agenda_item_pattern = re.compile(r"[-\*]? ?([\w\d \t\-,]*) \(?((?:\d{1,2}:)?\d?\d\:\d\d)\)?\n")
"""Pattern that matches agenda items with durations."""


@dataclass
class AgendaItem:
    name: str
    duration: timedelta

    active_since: datetime = None
    past_worktime: timedelta = timedelta()

    def start(self):
        self.active_since = datetime.now()

    def stop(self):
        self.past_worktime += time_passed(self.active_since)
        self.active_since = None

    @property
    def is_active(self):
        return self.active_since is not None

    @property
    def worktime(self) -> timedelta:
        if self.is_active:
            return self.past_worktime + time_passed(self.active_since)
        else:
            return self.past_worktime

    @property
    def delta(self) -> timedelta:
        return self.duration - self.worktime

    def __str__(self):
        return f"{self.name} ({self.duration})"

    def __post_init__(self):
        # strip leading and trailing whitespace from name
        self.name = self.name.strip()

        # parse duration string to timedelta
        if isinstance(self.duration, str):
            if len(self.duration) <= 5:
                time = datetime.strptime(self.duration, "%M:%S")
            else:
                time = datetime.strptime(self.duration, "%H:%M:%S")
            self.duration = timedelta(hours=time.hour, minutes=time.minute, seconds=time.second)


NOT_RUNNING = -1


@dataclass
class Agenda:
    title: str
    items: list[AgendaItem | str]

    @classmethod
    def loads(cls, content: str, title: str = None) -> "Agenda":
        if title is None:
            # try to read title from file content
            if content.splitlines()[0].startswith("#"):
                title = content.splitlines()[0][2:]
            else:
                title = None

        agenda_items = [AgendaItem(*match) for match in agenda_item_pattern.findall(content + "\n")]

        return cls(title, agenda_items)

    def __post_init__(self):
        if self.title:
            self.title = self.title.strip()

        # parse items to AgendaItems
        for idx, item in enumerate(self.items):
            if isinstance(item, str):
                logging.info("parsing '%s' to AgendaItem", item)
                self.items[idx] = AgendaItem(*agenda_item_pattern.search(item + "\n").groups())

    current_item_idx: int = NOT_RUNNING

    @property
    def current_item(self):
        if self.current_item_idx == NOT_RUNNING:
            return None
        return self.items[self.current_item_idx]

    @property
    def _next_item_available(self):
        return self.current_item_idx < len(self.items) - 1

    @property
    def delta(self):
        return self.delta_for(self.current_item_idx)

    def delta_for(self, idx: int):
        rv = timedelta()
        for item in self.items[:idx]:
            rv += item.delta
        return rv

    @property
    def _previous_item_available(self):
        return self.current_item_idx > 0

    def to_next(self) -> bool:
        """Go to next agenda item.

        Returns:
            Last agenda item was completed.
        """
        if self.current_item_idx >= 0:
            self.current_item.stop()
        if self._next_item_available:
            self.current_item_idx += 1
            self.current_item.start()
            return False
        return True

    def to_previous(self):
        """Go to previous agenda item."""
        if self.current_item_idx == NOT_RUNNING:
            return
        self.current_item.stop()
        if self._previous_item_available:
            self.current_item_idx -= 1
            self.current_item.start()
        else:
            self.current_item_idx = NOT_RUNNING


def time_passed(start: datetime, end: datetime = None) -> timedelta:
    if end is None:
        end = datetime.now()
    return end - start


def format_td(td: timedelta, positive_sign=True) -> str:
    sign = "-" if td < timedelta() else "+" if positive_sign else ""
    s = int(abs(td.total_seconds()))
    h, s = divmod(s, 3600)
    m, s = divmod(s, 60)
    rv = f"{m:02}:{s:02}"
    if h:
        rv = f"{h}:{rv}"
    rv = f"{sign}{rv}"
    return rv


def select_agenda_file(filepath: Path = Path.cwd()) -> str:
    if filepath is None:
        md_files = list(filepath.glob("*.md"))
        option, idx = pick.pick(md_files)
    return option


def format_agenda(agenda: Agenda):
    s = ""
    if agenda.title:
        s += f"{agenda.title}\n{len(agenda.title)*'-'}"
    max_len = min(max(len(item.name) for item in agenda.items), 40)
    for item in agenda.items:
        s += f"\n- {item.name:{max_len}s} ({item.duration})"
    return s


def print_agenda(agenda: Agenda):
    print(format_agenda(agenda))
