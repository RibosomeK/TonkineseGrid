from typing import Generic, TypeVar, Union, NoReturn
from dataclasses import dataclass

T = TypeVar("T")
E = TypeVar("E", bound=BaseException)


@dataclass
class Ok(Generic[T]):
    __slot__ = ("_value",)
    _value: T

    @property
    def value(self) -> T:
        return self._value

    def unwrap(self) -> T:
        return self._value

    def expect(self, msg: str = "") -> T:
        return self._value


@dataclass
class Err(Generic[E]):
    __slot__ = ("_err",)
    _err: E

    @property
    def value(self) -> E:
        return self._err

    def unwrap(self) -> NoReturn:
        raise self._err

    def expect(self, msg: str = "") -> NoReturn:
        try:
            self._err.add_note(msg)
        except AttributeError:
            if len(self._err.args) == 1:
                self._err.args = (f"{self._err.args[0]}\n{msg}",)
            else:
                print(msg)
        raise self._err


Result = Union[Ok[T], Err[E]]
