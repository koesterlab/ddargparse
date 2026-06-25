from ddargparse.field_interpretation import FieldInterpretation
from ddargparse.unions import UnionHandler
from typing import Sequence, Any, Iterable
from ddargparse.common import _raise_invalid
from ddargparse.enums import EnumArgTypeHandler
from inspect import isclass
from ddargparse.enums import EnumHandler
from enum import Enum
from functools import partial
from dataclasses import Field
import dataclasses
from dataclasses import dataclass, fields
from argparse import ArgumentParser, Namespace
from typing import Self, get_args, get_origin


@dataclass
class OptionsBase:
    """Base class for defining command-line options using dataclasses."""

    @classmethod
    def parse_args(
        cls, args: Sequence[str] | None = None, list_append: bool = False
    ) -> Self:
        """Parses command-line arguments and returns an instance of the dataclass."""

        parser = ArgumentParser(description=cls.__doc__)
        cls._managed_register_cli_args(parser, list_append=list_append)

        parsed_args = parser.parse_args(args)
        options = cls._from_cli_args(parsed_args, handle_subcommands=True)

        return options

    @classmethod
    def register_cli_args(
        cls, parser: ArgumentParser, list_append: bool = False
    ) -> None:
        cls._register_cli_args(
            parser, list_append=list_append, ignore_subcommand_fields=False
        )

    @classmethod
    def _register_cli_args(
        cls, parser: ArgumentParser, list_append: bool, ignore_subcommand_fields: bool
    ) -> None:
        """Registers command-line arguments based on the dataclass fields.

        Args:
            parser: An instance of argparse.ArgumentParser to which the arguments will be added.
            list_append: If True, non-positional list fields will use the 'append' action instead of 'nargs=+'.
        """
        for interpreted_field in cls.interpret_fields(ignore_subcommand_fields):
            arg_name = interpreted_field.name.replace(" ", "-")
            arg_type = interpreted_field.parse_method or interpreted_field.field_type

            kwargs = {
                "help": interpreted_field.help
            }

            if interpreted_field.is_optional:
                if not interpreted_field.parse_method:
                    arg_type = interpreted_field.optional_type
            elif interpreted_field.default is None and not interpreted_field.is_positional:
                kwargs["required"] = True

            if interpreted_field.field_type is bool:
                if interpreted_field.default is True:
                    arg_name = f"not-{arg_name}"
                    kwargs["action"] = "store_false"
                    kwargs["dest"] = interpreted_field.field_name
                else:
                    kwargs["action"] = "store_true"
            else:
                kwargs["default"] = interpreted_field.default

                if interpreted_field.is_list:
                    # TODO: test list in combination with parse_func
                    kwargs["type"] = interpreted_field.list_item_type
                    if list_append and not interpreted_field.is_positional:
                        kwargs["action"] = "append"
                    else:
                        kwargs["nargs"] = "+"
                else:
                    kwargs["type"] = arg_type

                if interpreted_field.metavar is not None:
                    kwargs["metavar"] = interpreted_field.metavar

            parser.add_argument(
                f"--{arg_name}" if not interpreted_field.is_positional else arg_name,
                **kwargs,
            )

    @classmethod
    def interpret_fields(
        cls, ignore_subcommand_fields: bool
    ) -> Iterable[FieldInterpretation]:
        """Interprets the dataclass fields and yields FieldInterpretation instances."""
        for cls_field in cls._cli_arg_fields(ignore_subcommand_fields):
            yield FieldInterpretation(cls, cls_field)

    @classmethod
    def from_cli_args(cls, args: Namespace) -> Self:
        """Creates an instance of the dataclass from the parsed command-line arguments."""
        return cls._from_cli_args(args, handle_subcommands=False)

    @classmethod
    def _from_cli_args(cls, args: Namespace, handle_subcommands: bool) -> Self:
        kwargs = {
            cls_field.name: getattr(args, cls_field.name)
            for cls_field in cls._cli_arg_fields(
                ignore_subcommand_fields=handle_subcommands
            )
        }

        if handle_subcommands:
            from ddargparse.subcommands import SubcommandHandler

            for cls_field in cls._subcommand_fields():
                handler = SubcommandHandler(cls_field)
                if args.subcommand == handler.subcommand_name():
                    subcommand_cls = handler.subcommand_options_cls()
                    subcommand_options = subcommand_cls._from_cli_args(
                        args, handle_subcommands=True
                    )
                    kwargs[cls_field.name] = subcommand_options
                else:
                    kwargs[cls_field.name] = None

        return cls(**kwargs)

    @classmethod
    def _subcommand_fields(cls) -> list[Field]:
        from ddargparse.subcommands import SubcommandHandler

        return [
            cls_field
            for cls_field in fields(cls)
            if SubcommandHandler(cls_field).is_subcommand_candidate()
        ]

    @classmethod
    def _cli_arg_fields(cls, ignore_subcommand_fields: bool) -> Iterable[Field]:
        from ddargparse.subcommands import SubcommandHandler

        if not ignore_subcommand_fields:
            return fields(cls)
        return (
            cls_field
            for cls_field in fields(cls)
            if not SubcommandHandler(cls_field).is_subcommand_candidate()
        )

    @classmethod
    def _managed_register_cli_args(
        cls, parser: ArgumentParser, list_append: bool
    ) -> None:
        """Creates and returns an ArgumentParser with registered arguments."""
        from ddargparse.subcommands import SubcommandHandler

        cls._register_cli_args(
            parser, list_append=list_append, ignore_subcommand_fields=True
        )
        subcommand_fields = cls._subcommand_fields()
        subparsers = None
        if subcommand_fields:
            subparsers = parser.add_subparsers(dest="subcommand")
        for cls_field in subcommand_fields:
            handler = SubcommandHandler(cls_field)

            subcommand_cls = handler.subcommand_options_cls()
            subcommand_name = handler.subcommand_name()

            assert subparsers is not None
            subparser = subparsers.add_parser(
                subcommand_name,
                description=handler.description(),
                help=handler.description(short=True),
            )
            subcommand_cls._managed_register_cli_args(
                subparser, list_append=list_append
            )
