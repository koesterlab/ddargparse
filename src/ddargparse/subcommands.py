from inspect import isclass
from ddargparse.options import _raise_invalid
from typing import get_args
from typing import Union
from dataclasses import dataclass, Field
from ddargparse.options import OptionsBase


@dataclass
class SubcommandHandler:
    field: Field

    def is_subcommand_candidate(self) -> bool:
        if isinstance(self.field.type, Union):
            cls = get_args(self.field.type)[0]
        else:
            cls = self.field.type
        return isclass(cls) and issubclass(cls, OptionsBase)

    def subcommand_name(self) -> str:
        return self.field.name.replace("_", "-")

    def description(self, short: bool = False) -> str | None:
        docstring = self.subcommand_options_cls().__doc__

        if not docstring:
            return None
        elif short:
            return docstring.split("\n")[0]
        else:
            return docstring

    def subcommand_options_cls(self) -> OptionsBase:
        subcommand_cls = self.field.type
        if not isinstance(subcommand_cls, Union) or get_args(subcommand_cls)[
            1
        ] is not type(None):
            self.raise_invalid(
                "Subcommand fields must be optional (e.g. subcommand_something: "
                "SubcommandOptions | None)."
            )

        return get_args(subcommand_cls)[0]

    def raise_invalid(self, message: str) -> None:
        _raise_invalid(message, cls_field=self.field)
