from processmap import __lib_name__, __version__


def test_version() -> None:
    assert __version__ == "0.1.0"


def test_lib_name() -> None:
    assert __lib_name__ == "processmap"
