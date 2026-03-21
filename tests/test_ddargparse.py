from enum import Enum
import pytest
from argparse import ArgumentParser
from dataclasses import dataclass, field

from ddargparse import OptionsBase


def make_parser(*option_classes, list_append: bool = False) -> ArgumentParser:
    """Build an ArgumentParser with all given OptionsBase subclasses registered."""
    parser = ArgumentParser()
    for cls in option_classes:
        cls.register_cli_args(parser, list_append=list_append)
    return parser


def parse(option_class, argv: list[str], list_append: bool = False):
    """Register, parse, and return an options instance from a argv list."""
    parser = make_parser(option_class, list_append=list_append)
    return option_class.from_cli_args(parser.parse_args(argv))


@dataclass
class SimpleOptions(OptionsBase):
    """The CLI description

    Some additonal line of description.
    """

    name: str | None = field(metadata={"help": "A name"})
    count: int = field(default=0, metadata={"help": "A count"})


@dataclass
class MultiTypeOptions(OptionsBase):
    id: str | int | None = field(default=3, metadata={"help": "An ID"})


@dataclass
class RequiredOptions(OptionsBase):
    output: str = field(metadata={"help": "Output path"})


@dataclass
class BoolOptions(OptionsBase):
    verbose: bool = field(metadata={"help": "Enable verbose mode"})
    quiet: bool = field(default=True, metadata={"help": "Suppress output"})


@dataclass
class BoolOptionsPositional(OptionsBase):
    verbose: bool = field(metadata={"help": "Enable verbose mode", "positional": True})


@dataclass
class BoolOptionsInvalidDefault(OptionsBase):
    verbose: bool = field(default=42, metadata={"help": "Enable verbose mode"})  # type: ignore


@dataclass
class ListOptions(OptionsBase):
    tags: list[str] = field(default_factory=list, metadata={"help": "One or more tags"})
    counts: list[int] = field(
        default_factory=list, metadata={"help": "One or more counts"}
    )


@dataclass
class PositionalOptions(OptionsBase):
    source: str = field(metadata={"help": "Source path", "positional": True})


@dataclass
class PositionalOptionalOptions(OptionsBase):
    source: str | None = field(metadata={"help": "Source path", "positional": True})


@dataclass
class UnderscoreOptions(OptionsBase):
    input_file: str | None = field(metadata={"help": "Input file path"})


@dataclass
class MetavarOptions(OptionsBase):
    path: str | None = field(metadata={"help": "A path", "metavar": "PATH"})


# patch docstring to increase test coverage
MetavarOptions.__doc__ = None


@dataclass
class CustomParseOptions(OptionsBase):
    pair: str | None = field(metadata={"help": "A key:value pair"})

    @classmethod
    def parse_pair(cls, value: str):
        key, _, val = value.partition(":")
        return (key, val)


class DummyEnum(Enum):
    ALPHA = 0
    BETA = 1
    GAMMA = 2


@dataclass
class EnumOptions(OptionsBase):
    mode: DummyEnum | None = field(metadata={"help": "An enum value"})
    mode2: DummyEnum = field(
        default=DummyEnum.ALPHA, metadata={"help": "Another enum value"}
    )


@dataclass
class InvalidEnumDefaultOptions(OptionsBase):
    mode: DummyEnum = field(default=42, metadata={"help": "An enum value"})  # type: ignore


@dataclass
class PureDataclassOptions(OptionsBase):
    """The CLI description

    Some additonal line of description.
    """

    value: str = field(metadata={"help": "A value"})
    do_foo: SimpleOptions | None
    do_bar: MetavarOptions | None


@dataclass
class PureDataclassInvalidSubcommandOptions(OptionsBase):
    """The CLI description

    Some additonal line of description.
    """

    value: str = field(metadata={"help": "A value"})
    do_foo: SimpleOptions | None
    do_bar: MetavarOptions


class TestSimpleOptions:
    def test_defaults_when_no_args(self):
        opts = parse(SimpleOptions, [])
        assert opts.name is None
        assert opts.count == 0

    def test_name_flag(self):
        opts = parse(SimpleOptions, ["--name", "alice"])
        assert opts.name == "alice"

    def test_count_flag(self):
        opts = parse(SimpleOptions, ["--count", "42"])
        assert opts.count == 42

    def test_count_is_int(self):
        opts = parse(SimpleOptions, ["--count", "7"])
        assert isinstance(opts.count, int)

    def test_both_flags(self):
        opts = parse(SimpleOptions, ["--name", "bob", "--count", "3"])
        assert opts.name == "bob"
        assert opts.count == 3


class TestMultiTypeOptions:
    def test_make_parser(self):
        with pytest.raises(
            ValueError,
            match="Union types with None are only allowed for single types with None",
        ):
            make_parser(MultiTypeOptions)


class TestRequiredOptions:
    def test_required_flag_provided(self):
        opts = parse(RequiredOptions, ["--output", "out.txt"])
        assert opts.output == "out.txt"

    def test_missing_required_flag_raises(self):
        parser = make_parser(RequiredOptions)
        with pytest.raises(SystemExit):
            parser.parse_args([])


class TestBoolOptions:
    def test_defaults(self):
        opts = parse(BoolOptions, [])
        assert opts.verbose is False
        assert opts.quiet is True

    def test_store_true(self):
        opts = parse(BoolOptions, ["--verbose"])
        assert opts.verbose is True

    def test_store_false(self):
        opts = parse(BoolOptions, ["--not-quiet"])
        assert opts.quiet is False

    def test_positional(self):
        with pytest.raises(ValueError, match="Boolean flags cannot be positional"):
            make_parser(BoolOptionsPositional)

    def test_invalid_default(self):
        with pytest.raises(
            ValueError,
            match="Boolean fields must have a default value of True or False",
        ):
            make_parser(BoolOptionsInvalidDefault)


class TestListOptions:
    def test_defaults(self):
        opts = parse(ListOptions, [])
        assert opts.tags == []
        assert opts.counts == []

    def test_single_tag(self):
        opts = parse(ListOptions, ["--tags", "alpha"])
        assert opts.tags == ["alpha"]

    def test_multiple_tags(self):
        opts = parse(ListOptions, ["--tags", "alpha", "beta", "gamma"])
        assert opts.tags == ["alpha", "beta", "gamma"]

    def test_int_list(self):
        opts = parse(ListOptions, ["--counts", "1", "2", "3"])
        assert opts.counts == [1, 2, 3]
        assert all(isinstance(c, int) for c in opts.counts)

    def test_list_append(self):
        opts = parse(
            ListOptions, ["--tags", "alpha", "--tags", "beta"], list_append=True
        )
        assert opts.tags == ["alpha", "beta"]


class TestPositionalOptions:
    def test_positional(self):
        opts = parse(PositionalOptions, ["myfile.txt"])
        assert opts.source == "myfile.txt"

    def test_positional_missing(self):
        parser = make_parser(PositionalOptions)
        with pytest.raises(SystemExit):
            parser.parse_args([])

    def test_no_flag_prefix(self):
        parser = make_parser(PositionalOptions)
        # Positional should not appear as --source
        help_text = parser.format_usage()
        assert "source" in help_text
        assert "--source" not in help_text


class TestPositionalOptionalOptions:
    def test_make_parser(self):
        with pytest.raises(ValueError, match="Positional arguments cannot be optional"):
            make_parser(PositionalOptionalOptions)


class TestUnderscoreOptions:
    def test_hyphenated_flag_accepted(self):
        opts = parse(UnderscoreOptions, ["--input-file", "data.csv"])
        assert opts.input_file == "data.csv"

    def test_underscore_flag_not_accepted(self):
        parser = make_parser(UnderscoreOptions)
        with pytest.raises(SystemExit):
            parser.parse_args(["--input_file", "data.csv"])


class TestMetavarOptions:
    def test_metavar_in_help(self):
        parser = make_parser(MetavarOptions)
        help_text = parser.format_help()
        assert "PATH" in help_text

    def test_value_parsed(self):
        opts = parse(MetavarOptions, ["--path", "/tmp/foo"])
        assert opts.path == "/tmp/foo"


class TestCustomParseOptions:
    def test_custom_parser_invoked(self):
        opts = parse(CustomParseOptions, ["--pair", "key:value"])
        assert opts.pair == ("key", "value")

    def test_custom_parser_empty_value(self):
        opts = parse(CustomParseOptions, ["--pair", "key:"])
        assert opts.pair == ("key", "")


class TestEnumOptions:
    def test_parsing(self):
        opts = parse(EnumOptions, ["--mode", "beta"])
        assert opts.mode == DummyEnum.BETA

    def test_default(self):
        opts = parse(EnumOptions, [])
        assert opts.mode is None
        assert opts.mode2 == DummyEnum.ALPHA

    def test_invalid_default(self):
        with pytest.raises(
            ValueError, match="Default value must be an instance of the enum."
        ):
            make_parser(InvalidEnumDefaultOptions)

    def test_invalid_choice(self):
        parser = make_parser(EnumOptions)
        with pytest.raises(SystemExit):
            parser.parse_args(["--mode", "delta"])


class TestPureDataclassMode:
    def test_subcommands(self):
        options = PureDataclassOptions.parse_args(
            ["--value", "test", "do-foo", "--name", "alice", "--count", "5"]
        )
        assert options.value == "test"
        assert options.do_foo is not None
        assert options.do_foo.name == "alice"
        assert options.do_foo.count == 5
        assert options.do_bar is None

    def test_invalid_subcommand(self):
        with pytest.raises(ValueError, match="Subcommand fields must be optional"):
            PureDataclassInvalidSubcommandOptions.parse_args(
                ["--value", "test", "do-bar", "--name", "alice", "--count", "5"]
            )
