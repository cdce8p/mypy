from typing import Generic, ParamSpec, TypeVar

T = TypeVar('T', default=int)

class Foo(Generic[T]):
    ...

reveal_type(Foo())
P = ParamSpec("P", default=(int,))
class Bar(Generic[P]):
    ...

reveal_type(Bar())
