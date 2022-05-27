from processmap.either import either


def test_either() -> None:
    assert either(1, 2) == 1


def test_either_with_none() -> None:
    assert either(None, 2) == 2


def test_either_with_zero() -> None:
    assert either(0, 2) == 0
