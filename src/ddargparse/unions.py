from dataclasses import dataclass
from ddargparse.common import _raise_invalid
from typing import get_args
import types
from typing import Union
from typing import get_origin
from dataclasses import Field


@dataclass
class UnionHandler:
    field: Field

    def is_union(self) -> bool:
        origin = get_origin(self.field.type)
        return origin is Union or origin is types.UnionType

    def union_contains_none(self) -> bool:
        return type(None) in get_args(self.field.type)

    def union_single_non_none_type(self) -> type:
        non_none_types = [t for t in get_args(self.field.type) if t is not type(None)]
        if len(non_none_types) != 1:
            _raise_invalid(
                "Union types with None are only allowed for single types with None (e.g. str | None).",
                cls_field=self.field,
            )
        return non_none_types[0]
