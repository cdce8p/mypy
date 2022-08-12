from typing import Callable, Generic, TypeVar  # noqa: F401
from typing_extensions import ParamSpec, TypeAlias, TypeVarTuple, Unpack, reveal_type  # noqa: F401

P = ParamSpec("P", default=[int, str])
P2 = ParamSpec("P2", default=P)
T = TypeVar("T", default=int)
T2 = TypeVar("T2", default=T)


class Foo(Generic[T, T2]): ...


reveal_type(Foo())
# reveal_type(Foo[str])
# partially1 = Foo
# partially = Foo[str]
# reveal_type(partially)
# reveal_type(partially[int])  # borked
# reveal_type(partially1)
# reveal_type(Foo[str, int])


class Bar(Generic[P, P2]): ...


reveal_type(Bar())

# def foo(fn: Callable[P, int]) -> bool:
#     ...
# reveal_type(foo)


# Ts = TypeVarTuple("Ts", default=Unpack[tuple[int, str]])


# class Spam(Generic[Unpack[Ts]]):
#     ...


# reveal_type(Spam())
# specialised: TypeAlias = "Foo[str]"
# specialised2: TypeAlias = "Foo[str, bool]"
# reveal_type(specialised())
# reveal_type(specialised2())
# P = ParamSpec("P", default=(int,))
# class Bar(Generic[P]):
#     ...

# reveal_type(Bar())

# reveal_type(Foo[int])
# reveal_type(specialised[int]())
# @dataclass
# class Box(Generic[T]):
#     value: T | None = None

# reveal_type(Box())                      # type is Box[int]
# reveal_type(Box(value="Hello World!"))  # type is Box[str]
