import tonkinese_grid
import textgrid
from timeit import timeit
import sys


def tg():
    textgrid.TextGrid.fromFile("./tests/sample/sample.TextGrid")


def custom_tg():
    tonkinese_grid.TextGrid.read("./tests/sample/sample.TextGrid")


def tg_save(tg):
    tg.write("./tests/sample/sample.TextGrid")


def custom_tg_save(tg):
    tg.save("./tests/sample/sample.TextGrid")


tg_file = textgrid.TextGrid.fromFile("./tests/sample/sample.TextGrid")
custom_tg_file = tonkinese_grid.TextGrid.read("./tests/sample/sample.TextGrid")


def main():
    print(sys.getsizeof(tg_file), sys.getsizeof(custom_tg_file))
    tg_read_10k = timeit("tg()", setup="from __main__ import tg", number=10000)
    custom_read_10k = timeit(
        "custom_tg()", setup="from __main__ import custom_tg", number=10000
    )
    print("Read from file for 10k times:")
    print(f"textgrid: {tg_read_10k}")
    print(f"tonkinese_grid: {custom_read_10k}")

    tg_save_10k = timeit(
        "tg_save(tg_file)", setup="from __main__ import tg_save, tg_file", number=10000
    )
    custom_tg_save_10k = timeit(
        "custom_tg_save(custom_tg_file)",
        setup="from __main__ import custom_tg_save, custom_tg_file",
        number=10000,
    )
    print("Save to file for 10k times:")
    print(f"textgrid: {tg_save_10k}")
    print(f"tonkinese_grid: {custom_tg_save_10k}")


if __name__ == "__main__":
    main()
