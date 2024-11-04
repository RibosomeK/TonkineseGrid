from tonkinese_grid import (
    Interval,
    IntervalList,
    IntervalTier,
    NotContinuousError,
    NotEnoughSpaceError,
    TextGrid,
    parse_text,
    parse_num,
)
import pytest


def test_parse():
    assert parse_text('text = "říkej ""ahoj"" dvakrát"').value == 'říkej "ahoj" dvakrát'
    assert parse_text('class = "IntervalTier"').value == "IntervalTier"
    assert parse_num("xmin = 0.0").value == 0.0
    assert parse_num("xmax = 2.3").value == 2.3


def test_interval():
    ivl1 = Interval(0, 1, "1")
    ivl1_1 = Interval(0, 1, "1")
    ivl2 = Interval(1, 2, "2")

    assert ivl1.min == 0
    assert ivl1.max == 1
    assert ivl1.text == "1"

    assert str(ivl1) == 'Interval: min = 0, max = 1, text = "1"'

    assert ivl1 == ivl1_1
    assert ivl1 != ivl2

    with pytest.raises(ValueError):
        ivl_err = Interval(2, 1, "err")

    assert Interval.is_continuous(ivl1, ivl2) == True
    assert Interval.is_continuous(ivl1, ivl1_1) == False


def test_interval_list():
    ivl = Interval(0, 1, "1")
    ivl_list = IntervalList()
    ivl_list.append(ivl)
    assert ivl_list[0].text == "1"
    with pytest.raises(NotContinuousError):
        ivl_list.append(Interval(0, 1, "not_continuous"))
    ivl_list.append(Interval(1, 2, "new_text"))
    assert ivl_list[1].text == "new_text"
    assert ivl_list[-1].text == "new_text"

    ivl_list.replace(0, "replaced")
    assert ivl_list[0].text == "replaced"

    with pytest.raises(IndexError):
        out_of_bound = ivl_list[100]

    with pytest.raises(IndexError):
        ivl_list.move_offset(0, 0.6)
    with pytest.raises(ValueError):
        ivl_list.move_offset(1, -0.5)
        ivl_list.move_offset(1, 3)
    ivl_list.move_offset(1, 0.6)
    assert ivl_list[0].min == 0
    assert ivl_list[0].max == 0.6
    assert ivl_list[1].min == 0.6
    assert ivl_list[1].max == 2

    with pytest.raises(IndexError):
        ivl_list.move_offset_by_dur(0, 0.1)
    with pytest.raises(ValueError):
        ivl_list.move_offset_by_dur(1, -0.7)
        ivl_list.move_offset_by_dur(1, 3)
    ivl_list.move_offset_by_dur(1, 0.2)
    assert ivl_list[0].min == 0
    assert Interval.is_continuous(ivl_list[0], ivl_list[1]) == True
    assert ivl_list[1].max == 2
    ivl_list.move_offset_by_dur(1, -0.2)
    assert ivl_list[0].min == 0
    assert Interval.is_continuous(ivl_list[0], ivl_list[1]) == True
    assert ivl_list[1].max == 2

    with pytest.raises(IndexError):
        ivl_list.merge(0, 3, "")
    with pytest.raises(ValueError):
        ivl_list.merge(0, 1, "")
    ivl_list.merge(0, 2, "merged")
    assert ivl_list.size() == 1
    assert ivl_list[0] == Interval(0, 2, "merged")

    with pytest.raises(NotEnoughSpaceError):
        ivl_list.split_insert(0, "inserted", 3)
    ivl_list.split_insert(0, "inserted", 0.3)
    assert ivl_list[0].text == "inserted"
    assert ivl_list.size() == 2
    assert Interval.is_continuous(ivl_list[0], ivl_list[1])
    assert ivl_list[0].min == 0
    assert ivl_list[-1].max == 2

    ivl_list.merge(0, 2, "merged")
    with pytest.raises(NotEnoughSpaceError):
        ivl_list.split_append(0, "appended", 3)
    ivl_list.split_append(0, "appended", 0.3)
    assert ivl_list[1].text == "appended"
    assert ivl_list.size() == 2
    assert Interval.is_continuous(ivl_list[0], ivl_list[1])
    assert ivl_list[0].min == 0
    assert ivl_list[-1].max == 2


def test_textgrid():
    tg = TextGrid.read("./tests/sample/full.TextGrid")
    assert tg.size() == 2
    assert tg.min == 0
    assert tg.max == 2.3
    assert tg[0].size() == 1
    assert tg[1].size() == 3
    assert tg[0][0] == Interval(0, 2.3, 'říkej "ahoj" dvakrát')
    assert tg[1][0] == Interval(0, 0.7, "r̝iːkɛj")
    assert tg[1][1] == Interval(0.7, 1.6, "ʔaɦɔj")
    assert tg[1][2] == Interval(1.6, 2.3, "dʋakraːt")

    with pytest.raises(ValueError):
        tg[0] = IntervalTier(-1, 3, "set item")
    tg[0] = IntervalTier(1, 3, "set item")
    assert tg[0].name == "set item"
    assert tg[0].min == 1
    assert tg[0].max == 3
    assert tg[0].intervals.size() == 0

    tg = TextGrid.read(
        "./tests/sample/short.TextGrid", format="short", encoding="utf_16_be"
    )
    tg.save("./tests/sample/short.TextGrid", format="short", encoding="utf_16_be")
