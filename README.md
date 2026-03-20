# ddargparse

A small Python library that lets you define command-line argument parsers using dataclasses.

## Installation

```bash
pip install ddargparse
```

## Usage

Subclass `OptionsBase` and annotate fields with standard argparse metadata via the `dataclasses.field` function (`help`, `required`, `positional`, `metavar`). Then call `register_cli_args` to populate an `ArgumentParser` and `from_cli_args` to instantiate your options from the parsed result.

```python
from argparse import ArgumentParser
from dataclasses import dataclass, field
from ddargparse import OptionsBase

@dataclass
class Options(OptionsBase):
    input: str = field(
        default=None,
        metadata={"help": "Input file", "required": True, "metavar": "FILE"},
    )
    verbose: bool = field(
        default=False,
        metadata={"help": "Enable verbose output"},
    )
    tags: list[str] = field(
        default_factory=list,
        metadata={"help": "One or more tags"},
    )

parser = ArgumentParser()
Options.register_cli_args(parser)
args = parser.parse_args()
options = Options.from_cli_args(args)
```

## Features

- Declare CLI arguments as typed dataclass fields — no repetitive `add_argument` calls, no need for the `type` argument.
- Booleans (`store_true` / `store_false`), and list arguments (`nargs="+"`) are inferred automatically from the dataclass field definitions.
- Custom parse methods: define a `parse_<field_name>` classmethod to override the argument type converter.
- Mark options as required (`"required": True`) or positional (`"positional": True`).
- No additional dependencies.

## Requirements

- Python ≥ 3.11

## License

See [LICENSE](LICENSE).
