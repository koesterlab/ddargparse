from ddargparse.common import is_any_type
from typing import Any
from typing import Callable
from typing import get_args
from typing import get_origin
from ddargparse.enums import EnumArgTypeHandler
from ddargparse.enums import EnumHandler
from enum import Enum
from inspect import isclass
import dataclasses
from ddargparse.unions import UnionHandler
from typing import Type
from ddargparse.common import _raise_invalid
from functools import partial
from dataclasses import Field


class FieldInterpretation:
    """Class for interpreting dataclass fields for command-line or UI argument registration."""

    def __init__(self, dataclass: type, cls_field: Field) -> None:
        raise_invalid = partial(_raise_invalid, cls_field=cls_field)

        if not is_any_type(cls_field.type):
            raise_invalid(
                "Field types may not be given as str and must be class names or "
                f"primitive types (found: {cls_field.type!r})."
            )
        self.field_type: Type = cls_field.type  # type: ignore

        self.is_positional: bool = cls_field.metadata.get("positional", False)
        self.field_name: str = cls_field.name
        self.name: str = self.field_name.replace("_", " ")
        self.parse_method: Callable | None = getattr(
            dataclass, f"parse_{cls_field.name}", None
        )
        self.is_optional: bool = False
        self.default: Any = None
        self.metavar: str | None = cls_field.metadata.get("metavar", None)
        self.help: str | None = cls_field.metadata.get("help")
        self.is_list: bool = False
        self.list_item_type: Type | None = None

        union_handler = UnionHandler(cls_field)

        if union_handler.is_union() and union_handler.union_contains_none():
            self.is_optional = True
            self.field_type = union_handler.union_single_non_none_type()

        if callable(cls_field.default_factory):
            self.default = cls_field.default_factory()
        elif cls_field.default is not None and not isinstance(
            cls_field.default, dataclasses._MISSING_TYPE
        ):
            self.default = cls_field.default

        if self.is_optional and self.is_positional:
            raise_invalid(
                "Positional arguments cannot be optional, remove the None "
                "in the type annotation or change to non-positional."
            )

        if self.field_type is bool:
            if self.is_positional:
                raise_invalid("Boolean flags cannot be positional.")
            if self.default is None:
                self.default = False
            if not isinstance(self.default, bool):
                raise_invalid(
                    "Boolean fields must have a default value of True or False."
                )
        else:
            if isclass(self.field_type) and issubclass(self.field_type, Enum):
                enum_handler = EnumHandler(self.field_type)
                if self.default is not None:
                    if isinstance(self.default, self.field_type):
                        self.default = enum_handler.item_to_choice(self.default)
                    else:
                        raise_invalid("Default value must be an instance of the enum.")
                if not self.parse_method:
                    self.metavar = enum_handler.metavar()
                self.parse_method = EnumArgTypeHandler(
                    cls_field, enum_handler, custom_parse_method=self.parse_method
                )

            if self.field_type is list or get_origin(self.field_type) is list:
                self.is_list = True
                self.list_item_type = get_args(self.field_type)[0]
