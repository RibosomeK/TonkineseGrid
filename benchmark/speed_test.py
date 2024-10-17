from timeit import timeit
import re

from tonkinese_grid import TextGrid

TEXT = 'text = "říkej ""ahoj"" dvakrát'
NUM = "xmax = 2.3"
LOOP = 100_000

# NUM_DIGHT = (
#     "0", "1", "2", "3" ,"4",
#     "5", "6", "7", "8", "9",
#     "."
# )

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
        f'File type = "ooTextFile"\n\
        Object class = "TextGrid"\n\
        \n\
        xmin = {tg.min}\n\
        xmax = {tg.max}\n'
    )
    
    if tg.size() == 0:
        string += "tiers? <absent>\n"
    else:
        string += f"tiers? <exists>\nsize = {tg.size()}\nitem []:\n"
    for idx, item in enumerate(tg.items):
        string += (
            f"{' ':4}item [{idx+1}]\n\
            {' ':8}class = \"IntervalTier\"\n\
            {' ':8}name = \"{item.name}\"\n\
            {' ':8}xmin = {item.min}\n\
            {' ':8}xmax = {item.max}\n\
            {' ':8}intervals: size = {item.size()}\n"
        )
        for jdx, ivl in enumerate(item):
            text = ivl.text.replace('"', '""')
            string += (
                f"{' ':12}intervals [{jdx+1}]\n\
                {' ':16}xmin = {ivl.min}\n\
                {' ':16}xmax = {ivl.max}\n\
                {' ':16}text = \"{text}\"\n"
            )
    return string

tg = TextGrid.read("./tests/sample/sample.TextGrid")

def plus_string():
    p_to_string(tg)
    
def format_string():
    f_to_string(tg)


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


if __name__ == "__main__":
    main()
