import types
from dataclasses import Field
from typing import Never


def _raise_invalid(message: str, cls_field: Field) -> Never:
    raise ValueError(f"{message} Invalid field: {cls_field.name}")


def is_any_type(obj):
    # Checks for standard classes, generic aliases (list[int]), and union types (int | str)
    return isinstance(obj, (type, types.GenericAlias, types.UnionType))
