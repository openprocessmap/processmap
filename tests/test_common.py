from processmap.common import fset


def test_fset() -> None:
    assert fset(1, 2, 3) == frozenset([1, 2, 3])
