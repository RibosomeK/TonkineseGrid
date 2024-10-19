from timeit import timeit
import re
import ctypes
from array import array
from superstring import SuperString
from stringzilla import Str

from tonkinese_grid import TextGrid

TEXT = 'text = "říkej ""ahoj"" dvakrát'
NUM = "xmax = 2.3"
LOOP = 100_000


NUMERIC_PATTERN = re.compile(r"(\w* *\w+) *= *([\d.]+)")
QUOTE_PATTERN = re.compile(r"(\w* *\w+) *= *\"(.*)\"")


def parse_num(line: str) -> float:
    if (match := NUMERIC_PATTERN.search(line)) is not None:
        return float(match.group(2))
    raise ValueError(line, "number")


def parse_text(line: str) -> str:
    if (match := QUOTE_PATTERN.search(line)) is not None:
        return match.group(2).replace('""', '"')
    raise ValueError(line, "quote text")


def rex_parse():
    parse_num(NUM)
    parse_text(TEXT)


def _parse_num(line: str) -> float:
    try:
        return float(line.split("=")[1].strip())
    except Exception:
        raise ValueError()


def _parse_text(line: str) -> str:
    try:
        return line.split("=")[1].strip().replace('""', '"')[1:-1]
    except Exception:
        raise ValueError()


def split_parse():
    _parse_num(NUM)
    _parse_text(TEXT)


def p_to_string(tg: TextGrid) -> str:
    string = (
        'File type = "ooTextFile"\n'
        + 'Object class = "TextGrid"\n'
        + "\n"
        + f"xmin = {tg.min}\n"
        + f"xmax = {tg.max}\n"
    )
    if tg.size() == 0:
        string += "tiers? <absent>\n"
    else:
        string += "tiers? <exists>\n" + f"size = {tg.size()}\n" + "item []:\n"
    for idx, item in enumerate(tg.items):
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


def f_to_string(tg: TextGrid) -> str:
    string = (
        f'File type = "ooTextFile"\n'
        'Object class = "TextGrid"\n'
        "\n"
        f"xmin = {tg.min}\n"
        f"xmax = {tg.max}\n"
    )

    if tg.size() == 0:
        string += "tiers? <absent>\n"
    else:
        string += f"tiers? <exists>\nsize = {tg.size()}\nitem []:\n"
    for idx, item in enumerate(tg.items):
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


def a_to_string(tg: TextGrid) -> str:
    string = array(
        "u",
        f'File type = "ooTextFile"\n'
        'Object class = "TextGrid"\n'
        "\n"
        f"xmin = {tg.min}\n"
        f"xmax = {tg.max}\n",
    )

    if tg.size() == 0:
        string.fromunicode("tiers? <absent>\n")
    else:
        string.fromunicode(f"tiers? <exists>\nsize = {tg.size()}\nitem []:\n")
    for idx, item in enumerate(tg.items):
        string.fromunicode(
            f"{' ':4}item [{idx+1}]\n"
            f"{' ':8}class = \"IntervalTier\"\n"
            f"{' ':8}name = \"{item.name}\"\n"
            f"{' ':8}xmin = {item.min}\n"
            f"{' ':8}xmax = {item.max}\n"
            f"{' ':8}intervals: size = {item.size()}\n"
        )
        for jdx, ivl in enumerate(item):
            text = ivl.text.replace('"', '""')
            string.fromunicode(
                f"{' ':12}intervals [{jdx+1}]\n"
                f"{' ':16}xmin = {ivl.min}\n"
                f"{' ':16}xmax = {ivl.max}\n"
                f"{' ':16}text = \"{text}\"\n"
            )
    return string.tounicode()


def c_to_string(tg: TextGrid) -> str:
    head = (
        f'File type = "ooTextFile"\n'
        'Object class = "TextGrid"\n'
        "\n"
        f"xmin = {tg.min}\n"
        f"xmax = {tg.max}\n"
    )
    start = len(head)
    buf = ctypes.create_unicode_buffer(head, 1300)
    if tg.size() == 0:
        text = "tiers? <absent>\n"
        buf[start : start + len(text)] = text
        start += len(text)
    else:
        text = f"tiers? <exists>\nsize = {tg.size()}\nitem []:\n"
        buf[start : start + len(text)] = text
        start += len(text)
    for idx, item in enumerate(tg.items):
        text = (
            f"{' ':4}item [{idx+1}]\n"
            f"{' ':8}class = \"IntervalTier\"\n"
            f"{' ':8}name = \"{item.name}\"\n"
            f"{' ':8}xmin = {item.min}\n"
            f"{' ':8}xmax = {item.max}\n"
            f"{' ':8}intervals: size = {item.size()}\n"
        )
        buf[start : start + len(text)] = text
        start += len(text)
        for jdx, ivl in enumerate(item):
            text = ivl.text.replace('"', '""')
            text = (
                f"{' ':12}intervals [{jdx+1}]\n"
                f"{' ':16}xmin = {ivl.min}\n"
                f"{' ':16}xmax = {ivl.max}\n"
                f"{' ':16}text = \"{text}\"\n"
            )
            buf[start : start + len(text)] = text
            start += len(text)
    return buf.value


def s_to_string(tg: TextGrid):
    string = SuperString(
        f'File type = "ooTextFile"\n'
        'Object class = "TextGrid"\n'
        "\n"
        f"xmin = {tg.min}\n"
        f"xmax = {tg.max}\n"
    )

    if tg.size() == 0:
        string += SuperString("tiers? <absent>\n")
    else:
        string += SuperString(f"tiers? <exists>\nsize = {tg.size()}\nitem []:\n")
    for idx, item in enumerate(tg.items):
        string += SuperString(
            f"{' ':4}item [{idx+1}]\n"
            f"{' ':8}class = \"IntervalTier\"\n"
            f"{' ':8}name = \"{item.name}\"\n"
            f"{' ':8}xmin = {item.min}\n"
            f"{' ':8}xmax = {item.max}\n"
            f"{' ':8}intervals: size = {item.size()}\n"
        )
        for jdx, ivl in enumerate(item):
            text = ivl.text.replace('"', '""')
            string += SuperString(
                f"{' ':12}intervals [{jdx+1}]\n"
                f"{' ':16}xmin = {ivl.min}\n"
                f"{' ':16}xmax = {ivl.max}\n"
                f"{' ':16}text = \"{text}\"\n"
            )
    return string


def z_to_string(tg: TextGrid):
    string = Str(
        f'File type = "ooTextFile"\n'
        'Object class = "TextGrid"\n'
        "\n"
        f"xmin = {tg.min}\n"
        f"xmax = {tg.max}\n"
    )

    if tg.size() == 0:
        string += "tiers? <absent>\n"
    else:
        string += f"tiers? <exists>\nsize = {tg.size()}\nitem []:\n"
    for idx, item in enumerate(tg.items):
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


def ba_to_string(tg: TextGrid):
    string = bytearray(3000)
    string.extend(
        map(
            ord,
            f'File type = "ooTextFile"\n'
            'Object class = "TextGrid"\n'
            "\n"
            f"xmin = {tg.min}\n"
            f"xmax = {tg.max}\n",
        )
    )

    if tg.size() == 0:
        string.extend(map(ord, "tiers? <absent>\n"))
    else:
        string.extend(map(ord, f"tiers? <exists>\nsize = {tg.size()}\nitem []:\n"))
    for idx, item in enumerate(tg.items):
        string.extend(
            map(
                ord,
                f"{' ':4}item [{idx+1}]\n"
                f"{' ':8}class = \"IntervalTier\"\n"
                f"{' ':8}name = \"{item.name}\"\n"
                f"{' ':8}xmin = {item.min}\n"
                f"{' ':8}xmax = {item.max}\n"
                f"{' ':8}intervals: size = {item.size()}\n",
            )
        )
        for jdx, ivl in enumerate(item):
            text = ivl.text.replace('"', '""')
            string.extend(
                map(
                    ord,
                    f"{' ':12}intervals [{jdx+1}]\n"
                    f"{' ':16}xmin = {ivl.min}\n"
                    f"{' ':16}xmax = {ivl.max}\n"
                    f"{' ':16}text = \"{text}\"\n",
                )
            )
    return string


class SaveString(ctypes.Structure):
    _fields_ = [
        ("text", ctypes.c_char_p),
        ("count", ctypes.c_size_t),
        ("capacity", ctypes.c_size_t),
    ]


def clib_to_string(tg: TextGrid):
    save_string = SaveString(0, 0, 0)
    sp = ctypes.pointer(save_string)
    lib = ctypes.CDLL("./src/save_string/bin/lib.so")
    lib.str_prealloc(sp, 5000)
    string = (
        f'File type = "ooTextFile"\n'
        'Object class = "TextGrid"\n'
        "\n"
        f"xmin = {tg.min}\n"
        f"xmax = {tg.max}\n"
    )
    lib.str_append(sp, string, len(string))
    if tg.size() == 0:
        lib.str_append(sp, "tiers? <absent>\n", 16)
    else:
        lib.str_append(sp, f"tiers? <exists>\nsize = {tg.size()}\nitem []:\n", 44)
    for idx, item in enumerate(tg.items):
        string = (
            f"{' ':4}item [{idx+1}]\n"
            f"{' ':8}class = \"IntervalTier\"\n"
            f"{' ':8}name = \"{item.name}\"\n"
            f"{' ':8}xmin = {item.min}\n"
            f"{' ':8}xmax = {item.max}\n"
            f"{' ':8}intervals: size = {item.size()}\n"
        )
        lib.str_append(sp, string, len(string))
        for jdx, ivl in enumerate(item):
            text = ivl.text.replace('"', '""')
            string = (
                f"{' ':12}intervals [{jdx+1}]\n"
                f"{' ':16}xmin = {ivl.min}\n"
                f"{' ':16}xmax = {ivl.max}\n"
                f"{' ':16}text = \"{text}\"\n"
            )
            lib.str_append(sp, string, len(string))


tg = TextGrid.read("./tests/sample/ascii.TextGrid")


def plus_string():
    p_to_string(tg)


def format_string():
    f_to_string(tg)


def array_string():
    a_to_string(tg)


def ctypes_string():
    c_to_string(tg)


def super_string():
    s_to_string(tg)


def zilla_string():
    z_to_string(tg)


def byte_string():
    ba_to_string(tg)


def clib_string():
    clib_to_string(tg)


def main():
    print(
        f'rex: {timeit("rex_parse()", setup="from __main__ import rex_parse", number=LOOP)}'
    )
    print(
        f'split: {timeit("split_parse()", setup="from __main__ import split_parse", number=LOOP)}'
    )
    print(
        f'plus: {timeit("plus_string()", setup="from __main__ import plus_string", number=LOOP)}'
    )
    print(
        f'format: {timeit("format_string()", setup="from __main__ import format_string", number=LOOP)}'
    )
    print(
        f'array: {timeit("array_string()", setup="from __main__ import array_string", number=LOOP)}'
    )
    print(
        f'ctypes: {timeit("ctypes_string()", setup="from __main__ import ctypes_string", number=LOOP)}'
    )
    print(
        f'superstring: {timeit("super_string()", setup="from __main__ import super_string", number=LOOP)}'
    )
    print(
        f'zillastring: {timeit("zilla_string()", setup="from __main__ import zilla_string", number=LOOP)}'
    )
    print(
        f'bytestring: {timeit("byte_string()", setup="from __main__ import byte_string", number=LOOP)}'
    )
    print(
        f'clib: {timeit("clib_string()", setup="from __main__ import clib_string", number=LOOP)}'
    )


if __name__ == "__main__":
    main()
