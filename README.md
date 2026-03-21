# ddargparse - dataclass driven argparse

[![test coverage: 100%](https://img.shields.io/badge/test%20coverage-100%25-green)](https://github.com/koesterlab/ddargparse/blob/main/pyproject.toml#L58)
![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/koesterlab/ddargparse/ci.yml?branch=main)
![PyPI](https://img.shields.io/pypi/v/ddargparse)

A small Python library that simplifies command-line argument parsing by leveraging dataclasses.
It allows developers to define their command-line interfaces using dataclass fields, making the code more concise and easier to maintain.
With ddargparse, you can easily create complex command-line applications with minimal boilerplate code.
It puts a particular focus on properly handling type annotations and defaults, minimizing additional required annotation and maintaining interoperability with the standard argparse.

## Installation

```bash
pip install ddargparse
```

## Usage

### Mode a: argparse + dataclasses

Subclass `OptionsBase` and annotate fields with standard argparse metadata via the `dataclasses.field` function (`help`, `required`, `positional`, `metavar`). Then call `register_cli_args` to populate an `ArgumentParser` and `from_cli_args` to instantiate your options from the parsed result.

#### Step 1: Option dataclass definition

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

@dataclass
class DoSomethingOptions(ddargparse.OptionsBase):
    threshold: str = field(metadata={"help": "Some threshold"})
    mode: SomeMode = field(default=SomeMode.DEFAULT, metadata={"help": "Mode to be used"})
```

#### Step 2: CLI argument parser declaration

```python
parser = ArgumentParser()
# register dataclass options as argparse parser arguments
Options.register_cli_args(parser)
subparsers = parser.add_subparsers(dest="subcommand")
subparser = subparsers.add_parser("do-something")
# register dataclass options as argparse subparser arguments
DoSomethingOptions.register_cli_args(subparser)
```

#### Step 3: CLI argument parsing and option dataclass instantiation

```python
args = parser.parse_args()
# obtain instance of dataclass with global options
options = Options.from_cli_args(args)
match args.subcommand:
    case "do-something":
        # obtain instance of dataclass with subcommand options
        do_something_options = DoSomethingOptions.from_cli_args(args)
```

### Mode b: dataclass only

In this mode, control over argparse is handed over to ddargparse entirely and happening under the hood.
The advantage is that subcommands can be expressed implicitly in the dataclass hierarchy.

#### Step 1: Option and subcommand dataclass definition

```python
from argparse import ArgumentParser
from dataclasses import dataclass, field
import ddargparse

@dataclass
class Options(ddargparse.OptionsBase):
    "The docstring is used as description in the CLI interface"

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
    subcommand_do_something: DoSomethingOptions | None

@dataclass
class DoSomethingOptions(ddargparse.OptionsBase):
    """This is the subcommand description
    
    The first line of the subcommand is used as short help, while the full description
    is displayed upon "mytool do-something --help"
    """

    threshold: str = field(metadata={"help": "Some threshold"})
    mode: SomeMode = field(default=SomeMode.DEFAULT, metadata={"help": "Mode to be used"})
```

#### Step 2: CLI argument parsing and option dataclass instantiation

Then, the entire hierarchy of options, including automatic determination of the
selected subcommand and its options can be obtained via calling `parse_args()` on the
top-level `Options` class.

```python
options = Options.parse_args()
```



## Features

- Declare CLI arguments as typed dataclass fields — no repetitive `add_argument` calls, no need for the `type` argument. Automatic convertion of field names into kebab-case CLI arguments.
- Booleans (`store_true` / `store_false`), and list arguments (`nargs="+"`) are inferred automatically from the dataclass field definitions.
- Custom parse methods: define a `parse_<field_name>` classmethod to override the argument type converter.
- Mark options as positional (`"positional": True`).
- Automatic and natural inference whether option is required (no `field(default=...)` and no `| None` in type annotation).
- Choose between append-style (`--arg item1 --arg item2 --arg item3`) and nargs-style (default, `--arg item1 item2 item3`) list arguments via `register_cli_args(..., list_append=True|False)` or `parse_args(list_append=True|False)`.
- Proper support for enums: simply specify an enum type and ddargparse handles ensures that proper (lower, kebab-cased) choices are inferred from the enum item names and the correct type is returned.
- Seamless integration with standard argparse API or dataclass only modes that hides all technical details of the argument parsing.
- No additional dependencies.

## Requirements

- Python ≥ 3.11

## License

See [LICENSE](LICENSE).
