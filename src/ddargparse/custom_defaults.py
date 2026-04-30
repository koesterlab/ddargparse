from ddargparse.subcommands import SubcommandHandler
from typing import get_args
from ddargparse.options import FieldSourceType
from ddargparse.common import _raise_invalid
from dataclasses import fields
from ddargparse.options import OptionsBase
from typing import Sequence
from dataclasses import dataclass
from typing import Mapping
from typing import Any


@dataclass
class CustomDefaultsHandler:
    custom_defaults: Sequence[Mapping[str, Any]]
    options_cls: OptionsBase

    def merge(self, mapping: Mapping[Any, Any], target: dict[Any, Any], options_cls: OptionsBase) -> None:
        """Merges a dictionary into the resolved dictionary, with the new
        dictionary overriding existing values.
        """
        cls_fields = {cls_field.name: cls_field for cls_field in fields(options_cls)}
        for key, value in mapping.items():
            cls_field = cls_fields.get(key)
            if cls_field is None:
                raise ValueError(f"Invalid custom default: no field named '{key}' in options class '{options_cls.__name__}'.")

            parse_method = options_cls._get_parse_method(cls_field.name, FieldSourceType.CUSTOM_DEFAULT)
            if parse_method is not None:
                target[key] = parse_method(value)
            else:
                subcommand_handler = SubcommandHandler(cls_field)
                if subcommand_handler.is_subcommand_candidate():
                    recurse_options_cls = subcommand_handler.subcommand_options_cls()
                else:
                    recurse_options_cls = options_cls

                self.merge(value, target[key], options_cls=recurse_options_cls)

    def resolve(self) -> dict[str, Any]:
        """Resolves multiple dictionaries into a single dictionary, with later
        dictionaries overriding earlier ones.
        
        This can be used to e.g. implement config-file/profile support, thereby
        choosing arbitrary serialization formats for the config files.
        """
        resolved = {}
        for mapping in self.custom_defaults:
            self.merge(mapping, target=resolved, options_cls=self.options_cls)

        return resolved