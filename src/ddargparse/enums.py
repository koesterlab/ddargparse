from dataclasses import Field
from ddargparse.common import _raise_invalid
from typing import Callable
from enum import Enum
from dataclasses import dataclass


@dataclass(frozen=True)
class EnumHandler[E: Enum]:
    enum_cls: type[E]

    def choice_to_item(self, choice: str) -> E:
        for item in self.enum_cls:
            if self.item_to_choice(item) == choice:
                return item
        raise ValueError(
            f"Invalid choice '{choice}' for enum {self.enum_cls.__name__}."
        )

    @classmethod
    def item_to_choice(cls, item: E) -> str:
        return item.name.replace("_", "-").lower()

    def choices(self) -> list[str]:
        return [self.item_to_choice(item) for item in self.enum_cls]

    def metavar(self) -> str:
        return f"{{{', '.join(self.choices())}}}"


@dataclass(frozen=True)
class EnumArgTypeHandler[E: Enum]:
    cls_field: Field
    enum_handler: EnumHandler[E]
    custom_parse_method: Callable[str, E] | None

    def __call__(self, choice: str) -> E:
        if self.custom_parse_method is not None:
            parsed = self.custom_parse_method(choice)
            if not isinstance(parsed, self.enum_handler.enum_cls):
                raise _raise_invalid(
                    "Custom parse method returned non-enum type "
                    f"{type(parsed)} instead of {E}"
                )
            return parsed
        return self.enum_handler.choice_to_item(choice)

    def __repr__(self) -> str:
        return self.cls_field.name
