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

    agenda2 = Agenda("test", items=["item 1 2:00", "item 2 1:00"])
    fp = util.get_filepath(agenda2, parent=tmp_path)
    assert fp.exists(), "same agenda title and items should yield same filepath"

    agenda3 = Agenda("different", items=["item 1 2:00", "item 2 1:00"])
    fp = util.get_filepath(agenda3, parent=tmp_path)
    assert not fp.exists(), "different agenda title should yield different filepath"

    agenda3 = Agenda("test", items=["item 3 12:00", "item 4 11:00"])
    fp = util.get_filepath(agenda3, parent=tmp_path)
    assert not fp.exists(), "different agenda items should yield different filepath"
