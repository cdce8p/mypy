from typing import Generic, ParamSpec, TypeAlias, TypeVar
from typing_extensions import reveal_type

T = TypeVar('T', default=int)
T2 = TypeVar('T2', default=list[T])

class Foo(Generic[T, T2]):
    bar: T2
reveal_type(Foo())

# specialised: TypeAlias = Foo[int]
# P = ParamSpec("P", default=(int,))
# class Bar(Generic[P]):
#     ...

# reveal_type(Bar())

# reveal_type(Foo[int])
# reveal_type(specialised)
# @dataclass
# class Box(Generic[T]):
#     value: T | None = None

# reveal_type(Box())                      # type is Box[int]
# reveal_type(Box(value="Hello World!"))  # type is Box[str]
