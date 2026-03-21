from ddargparse.unions import UnionHandler
from inspect import isclass
from ddargparse.options import _raise_invalid
from dataclasses import dataclass, Field
from ddargparse.options import OptionsBase


@dataclass
class SubcommandHandler:
    field: Field

    def is_subcommand_candidate(self) -> bool:
        union_handler = UnionHandler(self.field)
        if union_handler.is_union() and union_handler.union_contains_none():
            cls = union_handler.union_single_non_none_type()
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

    def subcommand_options_cls(self) -> type[OptionsBase]:
        union_handler = UnionHandler(self.field)
        if not union_handler.is_union() or not union_handler.union_contains_none():
            self.raise_invalid(
                "Subcommand fields must be optional (e.g. subcommand_something: "
                "SubcommandOptions | None)."
            )

        cls = union_handler.union_single_non_none_type()
        assert issubclass(cls, OptionsBase)
        return cls

    def raise_invalid(self, message: str) -> None:
        _raise_invalid(message, cls_field=self.field)
