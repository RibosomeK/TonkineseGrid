from dataclasses import dataclass, field
from typing import Iterator, Optional

from result import Ok, Err, Result


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
    ) -> "IntervalList":
        """extra methods to get rid of type error when using slice in __getitem__"""
        return IntervalList(self._data[start:stop:step])

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

    def extend(self, intervals: "IntervalList") -> None:
        """extend intervals from other IntervalList

        Raises:
            NotContinuousError: extending non continuous intervals
        """
        if not intervals:
            return
        if Interval.is_continuous(self[-1], intervals[0]):
            self._data.extend(intervals._data)
        else:
            raise NotContinuousError(self._data[-1], intervals[0])

    def extend_from(self, intervals: list[Interval]) -> None:
        """extend intervals from other list of Interval

        Raises:
            NotContinuousError: extending non continuous intervals
        """
        for ivl in intervals:
            self.append(ivl)

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
    ) -> IntervalList:
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

    def extend(self, intervals: IntervalList) -> None:
        """extend intervals from other IntervalList

        Raises:
            NotContinuousError: extending non continuous intervals
        """
        self.intervals.extend(intervals)

    def extend_from(self, intervals: list[Interval]) -> None:
        """extend intervals from other list of Interval

        Raises:
            NotContinuousError: extending non continuous intervals
        """
        self.intervals.extend_from(intervals)

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
            f'File type = "ooTextFile"\n'
            f'Object class = "TextGrid"\n'
            f"\n"
            f"xmin = {self.min}\n"
            f"xmax = {self.max}\n"
        )
        if self.size() == 0:
            string += "tiers? <absent>\n"
        else:
            string += f"tiers? <exists>\nsize = {self.size()}\nitem []:\n"
        for idx, item in enumerate(self.items):
            string += (
                f"{' ':4}item [{idx+1}]\n"
                f"{' ':8}class = \"IntervalTier\"\n"
                f"{' ':8}name = \"{item.name}\"\n"
                f"{' ':8}xmin = {item.min}\n"
                f"{' ':8}xmax = {item.max}\n"
                f"{' ':8}intervals: size = {item.size()}\n"
            )
            for jdx, ivl in enumerate(item):
                text = ivl.text.replace('"', '""')
                string += (
                    f"{' ':12}intervals [{jdx+1}]\n"
                    f"{' ':16}xmin = {ivl.min}\n"
                    f"{' ':16}xmax = {ivl.max}\n"
                    f"{' ':16}text = \"{text}\"\n"
                )
        return string

    def __repr__(self) -> str:
        string = (
            f'File type = "ooTextFile"\n'
            f'Object class = "TextGrid"\n'
            f"\n"
            f"{self.min}\n"
            f"{self.max}\n"
        )
        if self.size() == 0:
            string += "<absent>\n"
        else:
            string += f"<exists>\n{self.size()}\n"
        for item in self.items:
            string += (
                f'"IntervalTier"\n'
                f'"{item.name}"\n'
                f"{item.min}\n"
                f"{item.max}\n"
                f"{item.size()}\n"
            )
            for ivl in item:
                text = ivl.text.replace('"', '""')
                string += f"{ivl.min}\n" f"{ivl.max}\n" f'"{text}"\n'
        return string

    def __getitem__(self, idx: int) -> IntervalTier:
        return self.items[idx]

    def __setitem__(self, idx: int, tier: IntervalTier) -> None:
        self.items[idx] = tier

    @classmethod
    def read(
        cls, file: str, format: str = "full", encoding: str = "utf-8"
    ) -> "TextGrid":
        """read from a file. But `TextTier` is not supported.
        for more info please refer to [TextGrid file formats](https://www.fon.hum.uva.nl/praat/manual/TextGrid_file_formats.html)

        Exceptions:
            FileNotFoundError: cannot locate the file
            ParseError: failed to parse text labels or number labels
            SyntaxError: uncompleted TextGrid file like missing lines
            ValueError: loading TextGrid files which has TextTier class
        """
        if format == "full":
            return TextGrid.read_full(file, encoding)
        else:
            return TextGrid.read_short(file, encoding)

    @classmethod
    def read_full(cls, file: str, encoding: str = "utf-8") -> "TextGrid":
        with open(file, mode="r", encoding=encoding) as fp:
            lines = fp.readlines()
            textgrid = TextGrid(
                parse_num(
                    get_line(lines, 3).expect("Expect xmin line at line 4").strip()
                ).expect("At line 4"),
                parse_num(
                    get_line(lines, 4).expect("Expect xmax line, at line 5").strip()
                ).expect("At line 5"),
                [],
            )
            item_count = round(
                parse_num(
                    get_line(lines, 6).expect("Expect size line, at line 7").strip()
                ).expect("At line 7")
            )
            lines = get_iter(lines, 8).expect("Expect more lines at line 8")
            err_line_num = 9
            for _ in range(item_count):
                get_next(lines).expect(f"Expect index line at line {err_line_num}")
                class_type = parse_text(
                    get_next(lines)
                    .expect(f"Expect class line at line {err_line_num+1}")
                    .strip()
                ).expect(f"At line {err_line_num+1}")
                if class_type == "IntervalTier":
                    name = parse_text(
                        get_next(lines)
                        .expect(f"Expect name line at line {err_line_num+2}")
                        .strip()
                    ).expect(f"At line {err_line_num+2}")
                    min = parse_num(
                        get_next(lines)
                        .expect(f"Expect xmin line at line {err_line_num+3}")
                        .strip()
                    ).expect(f"At line {err_line_num+3}")
                    max = parse_num(
                        get_next(lines)
                        .expect(f"Expect xmax line at line {err_line_num+4}")
                        .strip()
                    ).expect(f"At line {err_line_num+4}")
                    ivl_count = round(
                        parse_num(
                            get_next(lines)
                            .expect(f"Expect size line at line {err_line_num+5}")
                            .strip()
                        ).expect(f"At line {err_line_num+5}")
                    )
                    tier = IntervalTier(min, max, name, IntervalList())
                    err_line_num += 6
                    for _ in range(ivl_count):
                        get_next(lines).expect(
                            f"Expect index line at line {err_line_num}"
                        )
                        min = parse_num(
                            get_next(lines)
                            .expect(f"Expect xmin line at line {err_line_num+1}")
                            .strip()
                        ).expect(f"At line {err_line_num+1}")
                        max = parse_num(
                            get_next(lines)
                            .expect(f"Expect xmax line at line {err_line_num+2}")
                            .strip()
                        ).expect(f"At line {err_line_num+2}")
                        text = parse_text(
                            get_next(lines)
                            .expect(f"Expect text line at line {err_line_num+3}")
                            .strip()
                        ).expect(f"At line {err_line_num+3}")
                        tier.append(Interval(min, max, text))
                        err_line_num += 4
                    textgrid.append(tier)
                else:
                    raise ValueError(f"Not Support Class: {class_type}")
            return textgrid

    @classmethod
    def read_short(cls, file: str, encoding: str = "utf-8") -> "TextGrid":
        with open(file, mode="r", encoding=encoding) as fp:
            lines = fp.readlines()
            textgrid = TextGrid(
                to_float(get_line(lines, 3).expect("Expect xmin line at line 4")),
                to_float(get_line(lines, 4).expect("Expect xmin line at line 5")),
            )
            item_count = to_int(get_line(lines, 6).expect("Expect size line at line 7"))
            lines = get_iter(lines, 7).expect("Expect more lines at lines 8")
            err_line_num = 8
            for _ in range(item_count):
                class_type = (
                    get_next(lines)
                    .expect(f"Expect class line at line {err_line_num}")
                    .strip()[1:-1]
                )
                if class_type == "IntervalTier":
                    name = (
                        get_next(lines)
                        .expect(f"Expect name line at line {err_line_num+1}")
                        .strip()[1:-1]
                    )
                    min = to_float(
                        get_next(lines).expect(
                            f"Expect xmin line at line {err_line_num+2}"
                        )
                    )
                    max = to_float(
                        get_next(lines).expect(
                            f"Expect xmax line at line {err_line_num+3}"
                        )
                    )
                    ivl_count = to_int(
                        get_next(lines).expect(
                            f"Expect size line at line {err_line_num+4}"
                        )
                    )
                    tier = IntervalTier(min, max, name)
                    err_line_num += 5
                    for _ in range(ivl_count):
                        min = to_float(
                            get_next(lines).expect(
                                f"Expect xmin line at line {err_line_num}"
                            )
                        )
                        max = to_float(
                            get_next(lines).expect(
                                f"Expect xmin line at line {err_line_num+1}"
                            )
                        )
                        text = (
                            get_next(lines)
                            .expect(f"Expect text line at line {err_line_num+2}")
                            .strip()[1:-1]
                            .replace('""', '"')
                        )
                        tier.append_new(min, max, text)
                        err_line_num += 3
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

    def save(self, path: str, format: str = "full", encoding: str = "utf-8") -> None:
        """save file to given location

        Exception:
            could be failed due to permission denied or given path is not valid
        """
        with open(path, mode="w", encoding=encoding) as fp:
            if format == "full":
                fp.write(str(self))
            else:
                fp.write(repr(self))

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
        super().__init__(f'Failed to parse line: "{line}" to get {t}')


def get_line(lines: list[str], idx: int) -> Result[str, SyntaxError]:
    try:
        return Ok(lines[idx])
    except IndexError:
        return Err(SyntaxError("Failed to get line"))


def get_iter(lines: list[str], start: int) -> Result[Iterator[str], SyntaxError]:
    try:
        return Ok(iter(lines[start:]))
    except IndexError:
        return Err(SyntaxError("Failed to get lines"))


def get_next(lines: Iterator[str]) -> Result[str, SyntaxError]:
    try:
        return Ok(next(lines))
    except StopIteration:
        return Err(SyntaxError("Fail to get next line"))


def parse_num(line: str) -> Result[float, ParseError]:
    try:
        return Ok(float(line.split("=")[1].strip()))
    except Exception as e:
        return Err(ParseError(line, f"number, due to {e}"))


def parse_text(line: str) -> Result[str, ParseError]:
    try:
        return Ok(line.split("=")[1].strip().replace('""', '"')[1:-1])
    except Exception as e:
        return Err(ParseError(line, f"text, due to {e}"))


def to_float(num_str: str) -> float:
    try:
        return float(num_str)
    except ValueError:
        raise ParseError(num_str, f"number")


def to_int(num_str: str) -> int:
    try:
        return int(num_str)
    except ValueError:
        raise ParseError(num_str, f"number")
