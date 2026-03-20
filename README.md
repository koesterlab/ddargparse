# ddargparse

A small Python library that simplifies command-line argument parsing by leveraging dataclasses.
It allows developers to define their command-line interfaces using dataclass fields, making the code more concise and easier to maintain.
With ddargparse, you can easily create complex command-line applications with minimal boilerplate code.
It puts a particular focus on properly handling type annotations and defaults, minimizing additional required annotation and maintaining interoperability with the standard argparse.

## Installation

```bash
pip install ddargparse
```

## Usage

Subclass `OptionsBase` and annotate fields with standard argparse metadata via the `dataclasses.field` function (`help`, `required`, `positional`, `metavar`). Then call `register_cli_args` to populate an `ArgumentParser` and `from_cli_args` to instantiate your options from the parsed result.

```python
from argparse import ArgumentParser
from dataclasses import dataclass, field
import ddargparse

@dataclass
class Options(ddargparse.OptionsBase):
    inputfile: str = field(
        metadata={"help": "Input file", "positional": True, "metavar": "FILE"},
    )
    verbose: bool = field(
        metadata={"help": "Enable verbose output"},
    )
    tags: list[str] = field(
        default_factory=list,
        metadata={"help": "One or more tags"},
    )

class DoSomethingOptions(ddargparse.OptionsBase):
    threshold: str = field(metadata={"help": "Some threshold"})

parser = ArgumentParser()
# register dataclass options as argparse parser arguments
Options.register_cli_args(parser)
subparsers = parser.add_subparsers(dest="subcommand")
subparser = subparsers.add_parser("do-something")
# register dataclass options as argparse subparser arguments
DoSomethingOptions.register_cli_args(subparser)

args = parser.parse_args()
# obtain instance of dataclass with global options
options = Options.from_cli_args(args)
match args.subcommand:
    case "do-something":
        # obtain instance of dataclass with subcommand options
        do_something_options = DoSomethingOptions.from_cli_args(args)
```

## Features

- Declare CLI arguments as typed dataclass fields — no repetitive `add_argument` calls, no need for the `type` argument.
- Booleans (`store_true` / `store_false`), and list arguments (`nargs="+"`) are inferred automatically from the dataclass field definitions.
- Custom parse methods: define a `parse_<field_name>` classmethod to override the argument type converter.
- Mark options as positional (`"positional": True`).
- Automatic and natural inference whether option is required (no `field(default=...)` and no `| None` in type annotation).
- Seamless integration with standard argparse API.
- No additional dependencies.

## Requirements

- Python ≥ 3.11

## License

See [LICENSE](LICENSE).
