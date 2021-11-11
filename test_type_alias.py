"""
Run file with
mypy --custom-typeshed-dir ../typeshed/ --show-traceback --no-incremental --strict test_type_alias.py
"""
from collections.abc import Sequence


def func(var: Sequence[str] = ("Hello",)) -> None:
    pass
