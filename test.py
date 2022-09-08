from typing import Callable, Generic, TypeVar
from typing_extensions import reveal_type, ParamSpec, TypeAlias

T = TypeVar("T", default=int)
T2 = TypeVar("T2", default=Callable[[T], int])


class Foo(Generic[T, T2]):
    bar: T2


reveal_type(Foo)
reveal_type(Foo[str])
partially1 = Foo
partially = Foo[str]
reveal_type(partially)
reveal_type(partially[int])
reveal_type(partially1)
reveal_type(Foo[str, int])

P = ParamSpec("P", default=[int, str])
def foo(fn: Callable[P, int]) -> bool: ...
reveal_type(foo)

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
