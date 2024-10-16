# TonkineseGrid for TextGrid file format

This is a python library that can read and write a **subset** of [TextGrid file format](https://www.fon.hum.uva.nl/praat/manual/TextGrid_file_formats.html), with full type hint, and some extra methods to manipulate intervals. 

**Notice that this library only support the full text format of TextGrid, and in which only contains IntervalTier class. Also this a side project has no full test of the codebase, therefore it is not production ready. Please use it at your own risk**

## Basic Usage

```python
from tonkinese_grid import TextGrid

textgrid = TextGrid.read("file.TextGrid")
for items in textgrid:
    for interval in items:
        print(interval)

new = TextGrid(0, 2.5)
new.append_new(0, 2.5, "words")
new[0].append_new(0, 1, "hello")
new[0].append_new(1, 2.5, "world")
new.save("HelloWorld.TextGrid")
```

## Classes And Methods

This section list basic information about the classes and their methods. For more details, please read the source code

```python
class Interval:
    min: float
    max: float
    text: str
    @staticmethod
    def is_continuous(prev: "Interval", curr: "Interval") -> bool:

class IntervalList:
    """a wrapper of list of intervals, which makes sure intervals inside of it
    is continuous and provide some other useful methods."""
    def __getitem__(self, idx: int) -> Interval: ...
    def __iter__(self) -> Iterator[Interval]: ...
    def __len__(self) -> int: ...
    def size(self) -> int: ...
    def slice(
        self,
        start: Optional[int] = None,
        stop: Optional[int] = None,
        step: Optional[int] = None,
    ) -> list[Interval]: ...
    def clear(self) -> None: ...
    def copy(self) -> IntervalList: ...
    def append(self, interval: Interval) -> None: ...
    def append_new(self, min: float, max: float, text: str) -> None: ...
    def replace(self, idx: int, text: str) -> None: ...
    def move_offset(self, idx: int, offset: float) -> None: ...
    def move_offset_by_dur(self, idx: int, dur: float) -> None: ...
    def split_insert(self, idx: int, text: str, dur: float) -> None: ...
    def split_append(self, idx: int, text: str, dur: float) -> None: ...
    def merge(self, start: int, end: int, text: str) -> None: ...

class IntervalTier:
    """Has the same methods with IntervalList"""
    min: float
    max: float
    name: str
    intervals: IntervalList

class TextGrid:
    min: float
    max: float
    items: list[IntervalTier]
    def __iter__(self) -> Iterator[IntervalTier]: ...
    def __str__(self) -> str: ...
    def __getitem__(self, idx: int) -> IntervalTier: ...
    def __setitem__(self, idx: int, tier: IntervalTier) -> None: ...
    @classmethod
    def read(cls, file: str) -> "TextGrid": ...
    def size(self) -> int: ...
    def copy(self) -> "TextGrid": ...
    def save(self, path: str) -> None: ...
    def append_new(self, min: float, max: float, name: str) -> None: ...
    def append(self, intervals: IntervalTier) -> None: ...
```

## Credit

[pytextgrid](https://github.com/kylebgorman/textgrid)