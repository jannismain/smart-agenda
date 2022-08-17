import time
from datetime import timedelta

import pytest

from smart_agenda.lib import NOT_RUNNING, Agenda, AgendaItem


@pytest.mark.parametrize(
    "params",
    [
        {"title": "Some Agenda", "items": ["first 1:00", "second 1:00:00"]},
        {"title": "Some Agenda", "items": [AgendaItem("first", "1:00"), AgendaItem("second", "1:00:00")]},
    ],
    ids=["from strings", "from AgendaItems"],
)
def test_agenda_init(params):
    expected_agenda = Agenda(
        "Some Agenda",
        [AgendaItem("first", timedelta(minutes=1)), AgendaItem("second", timedelta(hours=1))],
    )
    assert Agenda(**params) == expected_agenda


test_agenda_1 = """
# Test Agenda

First     12:00
Second 12:34:56
Third     00:01

While this line contains a duration (1:00) it should not be matched, as there is text afterwards...
""".lstrip()


def test_agenda_loads():
    agenda = Agenda.loads(test_agenda_1)
    assert agenda.title == "Test Agenda"
    assert len(agenda.items) == 3
    for item, expected in zip(
        agenda.items,
        [
            AgendaItem("First", timedelta(minutes=12)),
            AgendaItem("Second", timedelta(hours=12, minutes=34, seconds=56)),
            AgendaItem("Third", timedelta(seconds=1)),
        ],
    ):
        assert item == expected


def verify_current_item_idx(agenda, idx):
    assert agenda.current_item_idx == idx


def test_agenda_to_next():
    agenda = Agenda.loads(test_agenda_1)

    agenda.current_item is None
    verify_current_item_idx(agenda, NOT_RUNNING)

    assert not agenda.to_next()
    verify_current_item_idx(agenda, 0)
    assert agenda.current_item.is_active
    assert agenda.current_item == agenda.items[0]
    assert not agenda.items[1].is_active
    assert not agenda.items[2].is_active

    assert not agenda.to_next()
    verify_current_item_idx(agenda, 1)

    assert not agenda.to_next()
    verify_current_item_idx(agenda, 2)

    assert agenda.to_next(), "after last item, to_next should return done=True"
    assert agenda.current_item_idx == 2


def test_agenda_to_previous():
    agenda = Agenda.loads(test_agenda_1)
    agenda.to_next()
    agenda.to_next()
    verify_current_item_idx(agenda, 1)
    agenda.to_previous()
    verify_current_item_idx(agenda, 0)

    # going back beyond the first item should switch agenda into NOT_RUNNING state
    agenda.to_previous()
    verify_current_item_idx(agenda, NOT_RUNNING)

    # going back even more should not change current item
    agenda.to_previous()
    verify_current_item_idx(agenda, NOT_RUNNING)


def test_agenda_item_worktime():
    agenda = Agenda.loads(test_agenda_1)
    for item in agenda.items:
        assert item.worktime == timedelta(), "worktime should be zero initially"

    agenda.to_next()
    worktime = agenda.current_item.worktime
    assert worktime > timedelta(), "worktime should increase for current item"
    time.sleep(0.01)
    assert agenda.current_item.worktime > worktime, "worktime should increase with time"

    agenda.to_next()
    previous_item = agenda.items[agenda.current_item_idx - 1]
    previous_item_worktime = previous_item.worktime
    time.sleep(0.01)
    assert (
        previous_item_worktime == previous_item.worktime
    ), "worktime should not increase with time for items other than the current one"
