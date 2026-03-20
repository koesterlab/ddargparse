from dataclasses import Field
from typing import Never
import dataclasses
from typing import Union
from dataclasses import dataclass, fields
from argparse import ArgumentParser, Namespace
from typing import Self, get_args, get_origin


@dataclass
class OptionsBase:
    """Base class for defining command-line options using dataclasses."""

    @classmethod
    def register_cli_args(cls, parser: ArgumentParser) -> None:
        """Registers command-line arguments based on the dataclass fields."""
        for cls_field in fields(cls):

            def raise_invalid(message: str, cls_field: Field = cls_field) -> Never:
                raise ValueError(f"{message} Invalid field: {cls_field.name}")

            positional = cls_field.metadata.get("positional", False)

            arg_name = cls_field.name.replace("_", "-")

            parse_method = getattr(cls, f"parse_{cls_field.name}", None)
            field_type = cls_field.type

            if isinstance(field_type, Union) and type(None) in get_args(field_type):
                is_optional = True
                field_type = [t for t in get_args(field_type) if t is not type(None)]
                if len(field_type) > 1:
                    raise_invalid(
                        "Union types are only allowed for single types "
                        "with None (e.g. str | None)."
                    )
                else:
                    field_type = field_type[0]
            else:
                is_optional = False

            arg_type = parse_method or field_type

            default = None
            if callable(cls_field.default_factory):
                default = cls_field.default_factory()
            elif cls_field.default is not None and not isinstance(
                cls_field.default, dataclasses._MISSING_TYPE
            ):
                default = cls_field.default

            kwargs = {
                "help": cls_field.metadata["help"],
            }
            if is_optional:
                if positional:
                    raise_invalid(
                        "Positional arguments cannot be optional, remove the None "
                        "in the type annotation."
                    )
            elif arg_type is not bool and default is None and not positional:
                kwargs["required"] = True

            if arg_type is bool:
                if positional:
                    raise_invalid("Boolean flags cannot be positional.")
                if default is None:
                    default = False
                if not isinstance(default, bool):
                    raise_invalid(
                        "Boolean fields must have a default value of True or False."
                    )
                if default is True:
                    arg_name = f"not-{arg_name}"
                    kwargs["action"] = "store_false"
                    kwargs["dest"] = cls_field.name
                else:
                    kwargs["action"] = "store_true"

            else:
                kwargs["default"] = default
                if field_type is list or get_origin(field_type) is list:
                    kwargs["type"] = get_args(field_type)[0]
                    kwargs["nargs"] = "+"
                else:
                    kwargs["type"] = arg_type

            metavar = cls_field.metadata.get("metavar", None)
            if metavar is not None:
                kwargs["metavar"] = metavar

            parser.add_argument(
                f"--{arg_name}" if not positional else arg_name,
                **kwargs,
            )

    @classmethod
    def from_cli_args(cls, args: Namespace) -> Self:
        """Creates an instance of the dataclass from the parsed command-line arguments."""
        kwargs = {
            cls_field.name: getattr(args, cls_field.name) for cls_field in fields(cls)
        }
        return cls(**kwargs)
