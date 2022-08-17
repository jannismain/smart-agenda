from datetime import timedelta

import pytest

from smart_agenda.lib import Agenda, AgendaItem

test_agenda = """
# Title
First Item 12:00
Long Item 12:34:56
Item that uses brackets (00:01)
Item that uses tabs         45:00
  Item with leading whitespace  12:23

This should not be part of the agenda 12:12, despite the fact it might look like it.
""".lstrip()


def test_agenda_loads():
    agenda = Agenda.loads(test_agenda)
    expected_items = [
        AgendaItem("First Item", timedelta(minutes=12)),
        AgendaItem("Long Item", timedelta(hours=12, minutes=34, seconds=56)),
        AgendaItem("Item that uses brackets", timedelta(seconds=1)),
        AgendaItem("Item that uses tabs", timedelta(minutes=45)),
        AgendaItem("Item with leading whitespace", timedelta(minutes=12, seconds=23)),
    ]
    assert agenda.title == "Title"
    assert len(agenda.items) == len(expected_items)

    for idx, item in enumerate(agenda.items):
        assert agenda.items[idx].name == expected_items[idx].name
        assert agenda.items[idx].duration == expected_items[idx].duration


@pytest.mark.parametrize(
    "agenda_text,expected",
    [
        ("a 0:00", Agenda(None, [AgendaItem("a", timedelta(seconds=0))])),
        ("# Title\n", Agenda("Title", [])),
        ("# Title\nfoo 1:00", Agenda("Title", [AgendaItem("foo", timedelta(minutes=1))])),
    ],
)
def test_agenda_loads2(agenda_text, expected):
    assert Agenda.loads(agenda_text) == expected
