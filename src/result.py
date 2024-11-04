from typing import Generic, TypeVar, Union, NoReturn
from dataclasses import dataclass

T = TypeVar("T")
E = TypeVar("E", bound=BaseException)


@dataclass(slots=True)
class Ok(Generic[T]):
    _value: T

    @property
    def value(self) -> T:
        return self._value

    def unwrap(self) -> T:
        return self._value

    def expect(self, msg: str = "") -> T:
        return self._value


@dataclass(slots=True)
class Err(Generic[E]):
    _err: E

    @property
    def value(self) -> E:
        return self._err

    def unwrap(self) -> NoReturn:
        raise self._err

    def expect(self, msg: str = "") -> NoReturn:
        self._err.add_note(msg)
        raise self._err


Result = Union[Ok[T], Err[E]]
