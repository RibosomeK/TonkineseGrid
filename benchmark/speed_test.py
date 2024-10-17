from timeit import timeit
import re

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
    return float(line.split("=")[1].strip())


def _parse_text(line: str) -> str:
    return line.split("=")[1].strip().replace('""', '"')[1:-2]


def split_parse():
    _parse_num(NUM)
    _parse_text(TEXT)


def main():
    print(
        f'rex: {timeit("rex_parse()", setup="from __main__ import rex_parse", number=LOOP):>25}'
    )
    print(
        f'split: {timeit("split_parse()", setup="from __main__ import split_parse", number=LOOP):>23}'
    )


if __name__ == "__main__":
    main()
