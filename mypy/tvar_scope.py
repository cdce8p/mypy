from __future__ import annotations

from copy import copy
from typing import Iterator

from mypy.nodes import (
    ParamSpecExpr,
    SymbolTableNode,
    TypeVarExpr,
    TypeVarLikeExpr,
    TypeVarTupleExpr,
)
from mypy.type_visitor import SyntheticTypeVisitor
from mypy.types import (
    AnyType,
    CallableArgument,
    CallableType,
    DeletedType,
    EllipsisType,
    ErasedType,
    Instance,
    LiteralType,
    NoneType,
    Overloaded,
    Parameters,
    ParamSpecFlavor,
    ParamSpecType,
    PartialType,
    PlaceholderType,
    RawExpressionType,
    TupleType,
    TypeAliasType,
    TypedDictType,
    TypeList,
    TypeType,
    TypeVarId,
    TypeVarLikeType,
    TypeVarTupleType,
    TypeVarType,
    UnboundType,
    UninhabitedType,
    UnionType,
    UnpackType,
)


class TypeVarLikeYielder(SyntheticTypeVisitor[Iterator[TypeVarLikeType]]):
    """Yield all TypeVarLikeTypes in a type."""

    def visit_type_var(self, t: TypeVarType) -> Iterator[TypeVarLikeType]:
        yield t

    def visit_type_var_tuple(self, t: TypeVarTupleType) -> Iterator[TypeVarLikeType]:
        yield t

    def visit_param_spec(self, t: ParamSpecType) -> Iterator[TypeVarLikeType]:
        yield t

    def visit_callable_type(self, t: CallableType) -> Iterator[TypeVarLikeType]:
        for arg in t.arg_types:
            yield from arg.accept(self)
        yield from t.ret_type.accept(self)

    def visit_instance(self, t: Instance) -> Iterator[TypeVarLikeType]:
        for arg in t.args:
            yield from arg.accept(self)

    def visit_overloaded(self, t: Overloaded) -> Iterator[TypeVarLikeType]:
        for item in t.items:
            yield from item.accept(self)

    def visit_tuple_type(self, t: TupleType) -> Iterator[TypeVarLikeType]:
        for item in t.items:
            yield from item.accept(self)

    def visit_type_alias_type(self, t: TypeAliasType) -> Iterator[TypeVarLikeType]:
        for arg in t.args:
            yield from arg.accept(self)

    def visit_typeddict_type(self, t: TypedDictType) -> Iterator[TypeVarLikeType]:
        for arg in t.items.values():
            yield from arg.accept(self)

    def visit_union_type(self, t: UnionType) -> Iterator[TypeVarLikeType]:
        for arg in t.items:
            yield from arg.accept(self)

    def visit_type_type(self, t: TypeType) -> Iterator[TypeVarLikeType]:
        yield from t.item.accept(self)

    def visit_type_list(self, t: TypeList) -> Iterator[TypeVarLikeType]:
        yield from ()

    def visit_callable_argument(self, t: CallableArgument) -> Iterator[TypeVarLikeType]:
        yield from ()

    def visit_ellipsis_type(self, t: EllipsisType) -> Iterator[TypeVarLikeType]:
        yield from ()

    def visit_raw_expression_type(self, t: RawExpressionType) -> Iterator[TypeVarLikeType]:
        yield from ()

    def visit_unbound_type(self, t: UnboundType) -> Iterator[TypeVarLikeType]:
        yield from ()

    def visit_none_type(self, t: NoneType) -> Iterator[TypeVarLikeType]:
        yield from ()

    def visit_uninhabited_type(self, t: UninhabitedType) -> Iterator[TypeVarLikeType]:
        yield from ()

    def visit_erased_type(self, t: ErasedType) -> Iterator[TypeVarLikeType]:
        yield from ()

    def visit_deleted_type(self, t: DeletedType) -> Iterator[TypeVarLikeType]:
        yield from ()

    def visit_parameters(self, t: Parameters) -> Iterator[TypeVarLikeType]:
        yield from ()

    def visit_literal_type(self, t: LiteralType) -> Iterator[TypeVarLikeType]:
        yield from ()

    def visit_partial_type(self, t: PartialType) -> Iterator[TypeVarLikeType]:
        yield from ()

    def visit_unpack_type(self, t: UnpackType) -> Iterator[TypeVarLikeType]:
        yield from ()

    def visit_any(self, t: AnyType) -> Iterator[TypeVarLikeType]:
        yield from ()

    def visit_placeholder_type(self, t: PlaceholderType) -> Iterator[TypeVarLikeType]:
        yield from ()


class TypeVarLikeScope:
    """Scope that holds bindings for type variables and parameter specifications.

    Node fullname -> TypeVarLikeType.
    """

    def __init__(
        self,
        parent: TypeVarLikeScope | None = None,
        is_class_scope: bool = False,
        prohibited: TypeVarLikeScope | None = None,
        namespace: str = "",
    ) -> None:
        """Initializer for TypeVarLikeScope

        Parameters:
          parent: the outer scope for this scope
          is_class_scope: True if this represents a generic class
          prohibited: Type variables that aren't strictly in scope exactly,
                      but can't be bound because they're part of an outer class's scope.
        """
        self.scope: dict[str, TypeVarLikeType] = {}
        self.parent = parent
        self.func_id = 0
        self.class_id = 0
        self.is_class_scope = is_class_scope
        self.prohibited = prohibited
        self.namespace = namespace
        if parent is not None:
            self.func_id = parent.func_id
            self.class_id = parent.class_id

    def get_function_scope(self) -> TypeVarLikeScope | None:
        """Get the nearest parent that's a function scope, not a class scope"""
        it: TypeVarLikeScope | None = self
        while it is not None and it.is_class_scope:
            it = it.parent
        return it

    def allow_binding(self, fullname: str) -> bool:
        if fullname in self.scope:
            return False
        elif self.parent and not self.parent.allow_binding(fullname):
            return False
        elif self.prohibited and not self.prohibited.allow_binding(fullname):
            return False
        return True

    def method_frame(self) -> TypeVarLikeScope:
        """A new scope frame for binding a method"""
        return TypeVarLikeScope(self, False, None)

    def class_frame(self, namespace: str) -> TypeVarLikeScope:
        """A new scope frame for binding a class. Prohibits *this* class's tvars"""
        return TypeVarLikeScope(self.get_function_scope(), True, self, namespace=namespace)

    def new_unique_func_id(self) -> int:
        """Used by plugin-like code that needs to make synthetic generic functions."""
        self.func_id -= 1
        return self.func_id

    def bind_new(self, name: str, tvar_expr: TypeVarLikeExpr) -> TypeVarLikeType:
        if self.is_class_scope:
            self.class_id += 1
            i = self.class_id
        else:
            self.func_id -= 1
            i = self.func_id
        namespace = self.namespace
        # fix the namespace of any type vars
        default = tvar_expr.default

        for tv in default.accept(TypeVarLikeYielder()):
            tv = copy(tv)
            tv.id.namespace = namespace
            self.scope[tv.fullname] = tv
        if isinstance(tvar_expr, TypeVarExpr):
            tvar_def: TypeVarLikeType = TypeVarType(
                name=name,
                fullname=tvar_expr.fullname,
                id=TypeVarId(i, namespace=namespace),
                values=tvar_expr.values,
                upper_bound=tvar_expr.upper_bound,
                default=default,
                variance=tvar_expr.variance,
                line=tvar_expr.line,
                column=tvar_expr.column,
            )
        elif isinstance(tvar_expr, ParamSpecExpr):
            tvar_def = ParamSpecType(
                name,
                tvar_expr.fullname,
                i,
                flavor=ParamSpecFlavor.BARE,
                upper_bound=tvar_expr.upper_bound,
                default=default,
                line=tvar_expr.line,
                column=tvar_expr.column,
            )
        elif isinstance(tvar_expr, TypeVarTupleExpr):
            tvar_def = TypeVarTupleType(
                name,
                tvar_expr.fullname,
                i,
                upper_bound=tvar_expr.upper_bound,
                tuple_fallback=tvar_expr.tuple_fallback,
                default=default,
                line=tvar_expr.line,
                column=tvar_expr.column,
            )
        else:
            assert False
        self.scope[tvar_expr.fullname] = tvar_def
        return tvar_def

    def bind_existing(self, tvar_def: TypeVarLikeType) -> None:
        self.scope[tvar_def.fullname] = tvar_def

    def get_binding(self, item: str | SymbolTableNode) -> TypeVarLikeType | None:
        fullname = item.fullname if isinstance(item, SymbolTableNode) else item
        assert fullname
        if fullname in self.scope:
            return self.scope[fullname]
        elif self.parent is not None:
            return self.parent.get_binding(fullname)
        else:
            return None

    def __str__(self) -> str:
        me = ", ".join(f"{k}: {v.name}`{v.id}" for k, v in self.scope.items())
        if self.parent is None:
            return me
        return f"{self.parent} <- {me}"
