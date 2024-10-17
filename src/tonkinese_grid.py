from dataclasses import dataclass, field
from typing import Iterator, Optional


@dataclass(eq=True)
class Interval:
    __slots__ = ("min", "max", "text")
    min: float
    max: float
    text: str

    def __init__(self, min: float, max: float, text: str) -> None:
        if min >= max:
            raise ValueError(f"min: {min} cannot smaller or equal than max: {max}")
        if min < 0 or max < 0:
            raise ValueError(f"min: {min} and max: {max} must be real numbers")
        self.min = min
        self.max = max
        self.text = text
        pass

    def __str__(self) -> str:
        return f'Interval: min = {self.min}, max = {self.max}, text = "{self.text}"'

    @staticmethod
    def is_continuous(prev: "Interval", curr: "Interval") -> bool:
        """check if current interval has not gap to previous one

        Args:
            prev (Interval): interval that come first
            curr (Interval): interval that come later

        Returns:
            bool: True if they are continuous else False
        """
        return prev.max == curr.min

    def copy(self) -> "Interval":
        return Interval(self.min, self.max, self.text)


@dataclass
class IntervalList:
    _data: list[Interval] = field(default_factory=list)

    def __str__(self) -> str:
        return f"Intervals: {', '.join([str(ivl) for ivl in self._data])}"

    def __getitem__(self, idx: int) -> Interval:
        return self._data[idx]

    def __iter__(self) -> Iterator[Interval]:
        return iter(self._data)

    def __len__(self) -> int:
        return len(self._data)

    def size(self) -> int:
        """return the length of list, as same as builtin function len()"""
        return len(self._data)

    def slice(
        self,
        start: Optional[int] = None,
        stop: Optional[int] = None,
        step: Optional[int] = None,
    ) -> list[Interval]:
        """extra methods to get rid of type error when using slice in __getitem__"""
        return self._data[start:stop:step]

    def clear(self) -> None:
        """clear the list"""
        self._data.clear()

    def copy(self) -> "IntervalList":
        copy = IntervalList()
        copy._data = [ivl.copy() for ivl in self._data]
        return copy

    def append(self, interval: Interval) -> None:
        """append new interval, which should be continuous with previous one.

        Exceptions:
            NotContinuousError: appending non continuous interval
        """
        if self._data and not Interval.is_continuous(self._data[-1], interval):
            raise NotContinuousError(self._data[-1], interval)
        self._data.append(interval)

    def append_new(self, min: float, max: float, text: str) -> None:
        """append new interval by raw data

        Exceptions:
            NotContinuousError: appending non continuous interval
        """
        self.append(Interval(min, max, text))

    def replace(self, idx: int, text: str) -> None:
        """similar to `__setitem__`, but only replace the correspond text label,
        which makes more sense under the situation of the is interval list should be continuous

        Exceptions:
            IndexError: given index out of range
        """
        self._data[idx].text = text

    def move_offset(self, idx: int, offset: float) -> None:
        """move the start offset to the given value.

        Exceptions:
            ValueError: given offset goes beyond the max time of current interval
            or the min time of previous interval
        """
        if idx == 0:
            raise IndexError("Moving first interval's offset is not supported")

        prev, curr = self[idx - 1], self[idx]
        if prev.min < offset and offset < curr.max:
            curr.min = offset
            prev.max = offset
        else:
            raise ValueError(
                f"Offset: {offset} should lay between the min time of previous interval: {prev} and the max time of current one: {curr}"
            )

    def move_offset_by_dur(self, idx: int, dur: float) -> None:
        """similar to `move_offset`. dur can be positive which move the start offset bigger (to the right on graph),
        or negative which move the start offset smaller (to the left on graph)

        Exceptions:
            ValueError: given duration makes the changed offset goes beyond the max time of current interval
            or the min time of previous interval
        """
        offset = self[idx].min + dur
        self.move_offset(idx, offset)

    def split_insert(self, idx: int, text: str, dur: float) -> None:
        """split given interval into two and insert new interval as follow:

        ```
        old: | interval | -> new: | insert one | interval |
                                  |<-   dur  ->|
        ```

        Exceptions:
            NotEnoughSpaceError: given duration is larger or equal to the interval
        """
        curr = self[idx]
        if dur >= curr.max - curr.min:
            raise NotEnoughSpaceError(curr, dur)
        inserted = Interval(curr.min, curr.max + dur, text)
        curr.min = inserted.max
        self._data.insert(idx, inserted)

    def split_append(self, idx: int, text: str, dur: float) -> None:
        """split given interval into two and append new interval as follow:


        ```
        old: | interval | -> new: | interval | append one |
                                             |<-   dur  ->|
        ```

        Exceptions:
            NotEnoughSpaceError: given duration is larger or equal to the interval
        """
        curr = self[idx]
        if dur >= curr.max - curr.min:
            raise NotEnoughSpaceError(curr, dur)
        appended = Interval(curr.max - dur, curr.max, text)
        curr.max = appended.min
        if idx == -1 or idx == self.size() - 1:
            self.append(appended)
        else:
            self._data.insert(idx + 1, appended)

    def merge(self, start: int, end: int, text: str) -> None:
        """merge intervals from start index to end (not included),
        and change that first interval text to the given one.

        Exceptions:
            IndexError: given index out of range
            ValueError: less than two intervals being merged
        """
        if end - start < 2:
            raise ValueError(
                f"Invalid start: {start} and end: {end}, You should at least merge two intervals"
            )
        self[start].max = self[end - 1].max
        self[start].text = text
        self._data = self._data[: start + 1] + self._data[end:]


@dataclass
class IntervalTier:
    min: float
    max: float
    name: str
    intervals: IntervalList

    def __init__(
        self,
        min: float,
        max: float,
        name: str,
        intervals: Optional[IntervalList] = None,
    ) -> None:
        if min >= max:
            raise ValueError(f"min: {min} cannot smaller or equal than max: {max}")
        if min < 0 or max < 0:
            raise ValueError(f"min: {min} and max: {max} must be real numbers")
        self.min = min
        self.max = max
        self.name = name
        self.intervals = intervals if intervals is not None else IntervalList()

    def __len__(self) -> int:
        return self.intervals.size()

    def __iter__(self) -> Iterator[Interval]:
        return iter(self.intervals)

    def __getitem__(self, idx: int):
        return self.intervals[idx]

    def size(self) -> int:
        """return the length of list, as same as builtin function len()"""
        return self.intervals.size()

    def slice(
        self,
        start: Optional[int] = None,
        stop: Optional[int] = None,
        step: Optional[int] = None,
    ) -> list[Interval]:
        return self.intervals.slice(start, stop, step)

    def copy(self) -> "IntervalTier":
        return IntervalTier(self.min, self.max, self.name, self.intervals.copy())

    def clear(self) -> None:
        self.intervals.clear()

    def append(self, interval: Interval) -> None:
        """append new interval, which should be continuous with previous one.

        Exceptions:
            ValueError: appending non continuous interval
        """
        self.intervals.append(interval)

    def append_new(self, min: float, max: float, text: str) -> None:
        """append new interval by raw data

        Exceptions:
            ValueError: appending non continuous interval
        """
        self.intervals.append_new(min, max, text)

    def replace(self, idx: int, text: str) -> None:
        """similar to `__setitem__`, but only replace the correspond text label,
        which makes more sense under the situation of the is interval list should be continuous

        Exceptions:
            IndexError: given index out of range
        """
        self.intervals.replace(idx, text)

    def move_offset(self, idx: int, offset: float) -> None:
        """move the start offset to the given value.

        Exceptions:
            ValueError: given offset goes beyond the max time of current interval
            or the min time of previous interval
        """
        self.intervals.move_offset(idx, offset)

    def move_offset_by_dur(self, idx: int, dur: float) -> None:
        """similar to `move_offset`. dur can be positive which move the start offset bigger (to the right on graph),
        or negative which move the start offset smaller (to the left on graph)

        Exceptions:
            NotEnoughSpace: given duration makes the changed offset goes beyond the max time of current interval
            or the min time of previous interval
        """
        self.intervals.move_offset_by_dur(idx, dur)

    def split_insert(self, idx: int, text: str, dur: float) -> None:
        """split given interval into two and insert new interval as follow:

        ```
        old: | interval | -> new: | insert one | interval |
                                  |<-   dur  ->|
        ```

        Exceptions:
            NotEnoughSpace: given duration is larger or equal to the interval
        """
        self.intervals.split_insert(idx, text, dur)

    def split_append(self, idx: int, text: str, dur: float) -> None:
        """split given interval into two and append new interval as follow:


        ```
        old: | interval | -> new: | interval | append one |
                                             |<-   dur  ->|
        ```

        Exceptions:
            ValueError: given duration is larger or equal to the interval
        """
        self.intervals.split_append(idx, text, dur)

    def merge(self, start: int, end: int, text) -> None:
        """merge intervals from start index to end (not included),
        and change that first interval text to the given one.

        Exceptions:
            IndexError: given index out of range
            ValueError: less than two intervals being merged
        """
        self.intervals.merge(start, end, text)


@dataclass
class TextGrid:
    min: float
    max: float
    items: list[IntervalTier]

    def __init__(
        self, min: float, max: float, items: Optional[list[IntervalTier]] = None
    ) -> None:
        if min >= max:
            raise ValueError(f"min: {min} cannot smaller or equal than max: {max}")
        if min < 0 or max < 0:
            raise ValueError(f"min: {min} and max: {max} must be real numbers")
        self.min = min
        self.max = max
        self.items = items if items is not None else []

    def __iter__(self) -> Iterator[IntervalTier]:
        return iter(self.items)

    def __len__(self) -> int:
        return len(self.items)

    def __str__(self) -> str:
        string = (
            'File type = "ooTextFile"\n'
            + 'Object class = "TextGrid"\n'
            + "\n"
            + f"xmin = {self.min}\n"
            + f"xmax = {self.max}\n"
        )
        if self.size() == 0:
            string += "tiers? <absent>\n"
        else:
            string += "tiers? <exists>\n" + f"size = {self.size()}\n" + "item []:\n"
        for idx, item in enumerate(self.items):
            string += (
                f"{' ':4}item [{idx+1}]\n"
                + f"{' ':8}class = \"IntervalTier\"\n"
                + f"{' ':8}name = \"{item.name}\"\n"
                + f"{' ':8}xmin = {item.min}\n"
                + f"{' ':8}xmax = {item.max}\n"
                + f"{' ':8}intervals: size = {item.size()}\n"
            )
            for jdx, ivl in enumerate(item):
                text = ivl.text.replace('"', '""')
                string += (
                    f"{' ':12}intervals [{jdx+1}]\n"
                    + f"{' ':16}xmin = {ivl.min}\n"
                    + f"{' ':16}xmax = {ivl.max}\n"
                    + f"{' ':16}text = \"{text}\"\n"
                )
        return string

    def __getitem__(self, idx: int) -> IntervalTier:
        return self.items[idx]

    def __setitem__(self, idx: int, tier: IntervalTier) -> None:
        self.items[idx] = tier

    @classmethod
    def read(cls, file: str) -> "TextGrid":
        """read from a file. currently only support `full text format`,
        and `TextTier` is not supported. for more info please refer to [TextGrid file formats](https://www.fon.hum.uva.nl/praat/manual/TextGrid_file_formats.html)

        Exceptions:
            FileNotFoundError: cannot locate the file
            SyntaxError: failed to parse text labels or number labels
            ValueError: loading unsupported TextGrid file format
        """
        with open(file, mode="r", encoding="utf-8") as fp:
            lines = fp.readlines()
            textgrid = TextGrid(
                parse_num(lines[3].strip()), parse_num(lines[4].strip()), []
            )

            item_count = round(parse_num(lines[6].strip()))
            lines = iter(lines[8:])
            for _ in range(item_count):
                next(lines)
                class_type = parse_text(next(lines).strip())
                if class_type == "IntervalTier":
                    name = parse_text(next(lines).strip())
                    min = parse_num(next(lines).strip())
                    max = parse_num(next(lines).strip())
                    ivl_count = round(parse_num(next(lines).strip()))
                    tier = IntervalTier(min, max, name, IntervalList())
                    for _ in range(ivl_count):
                        next(lines)
                        min = parse_num(next(lines).strip())
                        max = parse_num(next(lines).strip())
                        text = parse_text(next(lines).strip())
                        tier.append(Interval(min, max, text))
                    textgrid.append(tier)
                else:
                    raise ValueError(f"Not Support Class: {class_type}")
            return textgrid

    def size(self) -> int:
        """how many items in the file, as same as the builtin `len()`"""
        return len(self.items)

    def copy(self) -> "TextGrid":
        """return a full copy of TextGrid object"""
        return TextGrid(self.min, self.max, [item.copy() for item in self.items])

    def save(self, path: str) -> None:
        """save file to given location

        Exception:
            could be failed due to permission denied or given path is not valid
        """
        with open(path, mode="w", encoding="utf-8") as fp:
            fp.write(str(self))

    def append_new(self, min: float, max: float, name: str) -> None:
        """append new interval tier from raw data"""
        self.items.append(IntervalTier(min, max, name, IntervalList()))

    def append(self, intervals: IntervalTier) -> None:
        """append new interval tier"""
        self.items.append(intervals)


class NotContinuousError(Exception):
    def __init__(self, prev: Interval, curr: Interval) -> None:
        super().__init__(
            f"Previous interval: {prev} is not continuous with current one: {curr}"
        )


class NotEnoughSpaceError(Exception):
    def __init__(self, interval: Interval, dur: float) -> None:
        super().__init__(
            f"Interval: {interval} to be splitted has not enough space for duration: {dur}"
        )


class ParseError(Exception):
    def __init__(self, line: str, t: str) -> None:
        super().__init__(f"Failed to parse line: {line} to get {t}")


def parse_num(line: str) -> float:
    try:
        return float(line.split("=")[1].strip())
    except Exception as e:
        raise ParseError(line, f"number, due to {e}")


def parse_text(line: str) -> str:
    try:
        return line.split("=")[1].strip().replace('""', '"')[1:-1]
    except Exception as e:
        raise ParseError(line, f"text, due to {e}")
