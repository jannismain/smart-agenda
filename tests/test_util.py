from pathlib import Path

from smart_agenda import util
from smart_agenda.lib import Agenda


def test_get_filepath(tmp_path):
    agenda = Agenda("test", items=["item 1 2:00", "item 2 1:00"])
    fp = util.get_filepath(agenda, parent=tmp_path)
    assert isinstance(fp, Path)


def test_get_filepath_when_existing(tmp_path):
    agenda = Agenda("test", items=["item 1 2:00", "item 2 1:00"])
    fp = util.get_filepath(agenda, parent=tmp_path)
    fp.touch()
    assert fp.exists()

    fp = util.get_filepath(agenda, parent=tmp_path)
    assert isinstance(fp, Path)
    assert not fp.exists(), "a unique filename should be provided"
