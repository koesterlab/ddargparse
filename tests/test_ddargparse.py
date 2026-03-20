"""Tests for ddargparse.OptionsBase."""

import pytest
from argparse import ArgumentParser
from dataclasses import dataclass, field

from ddargparse import OptionsBase


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def make_parser(*option_classes):
    """Build an ArgumentParser with all given OptionsBase subclasses registered."""
    parser = ArgumentParser()
    for cls in option_classes:
        cls.register_cli_args(parser)
    return parser


def parse(option_class, argv: list[str]):
    """Register, parse, and return an options instance from a argv list."""
    parser = make_parser(option_class)
    return option_class.from_cli_args(parser.parse_args(argv))


# ---------------------------------------------------------------------------
# Fixtures / shared option dataclasses
# ---------------------------------------------------------------------------


@dataclass
class SimpleOptions(OptionsBase):
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


@dataclass
class CustomParseOptions(OptionsBase):
    pair: str | None = field(metadata={"help": "A key:value pair"})

    @classmethod
    def parse_pair(cls, value: str):
        key, _, val = value.partition(":")
        return (key, val)


# ---------------------------------------------------------------------------
# Tests: optional flags and defaults
# ---------------------------------------------------------------------------


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
            ValueError, match="Union types are only allowed for single types with None"
        ):
            make_parser(MultiTypeOptions)


# ---------------------------------------------------------------------------
# Tests: required flags
# ---------------------------------------------------------------------------


class TestRequiredOptions:
    def test_required_flag_provided(self):
        opts = parse(RequiredOptions, ["--output", "out.txt"])
        assert opts.output == "out.txt"

    def test_missing_required_flag_raises(self):
        parser = make_parser(RequiredOptions)
        with pytest.raises(SystemExit):
            parser.parse_args([])


# ---------------------------------------------------------------------------
# Tests: boolean flags
# ---------------------------------------------------------------------------


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


# ---------------------------------------------------------------------------
# Tests: list arguments
# ---------------------------------------------------------------------------


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


# ---------------------------------------------------------------------------
# Tests: positional arguments
# ---------------------------------------------------------------------------


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


# ---------------------------------------------------------------------------
# Tests: underscore → hyphen conversion
# ---------------------------------------------------------------------------


class TestUnderscoreOptions:
    def test_hyphenated_flag_accepted(self):
        opts = parse(UnderscoreOptions, ["--input-file", "data.csv"])
        assert opts.input_file == "data.csv"

    def test_underscore_flag_not_accepted(self):
        parser = make_parser(UnderscoreOptions)
        with pytest.raises(SystemExit):
            parser.parse_args(["--input_file", "data.csv"])


# ---------------------------------------------------------------------------
# Tests: metavar
# ---------------------------------------------------------------------------


class TestMetavarOptions:
    def test_metavar_in_help(self):
        parser = make_parser(MetavarOptions)
        help_text = parser.format_help()
        assert "PATH" in help_text

    def test_value_parsed(self):
        opts = parse(MetavarOptions, ["--path", "/tmp/foo"])
        assert opts.path == "/tmp/foo"


# ---------------------------------------------------------------------------
# Tests: custom parse method
# ---------------------------------------------------------------------------


class TestCustomParseOptions:
    def test_custom_parser_invoked(self):
        opts = parse(CustomParseOptions, ["--pair", "key:value"])
        assert opts.pair == ("key", "value")

    def test_custom_parser_empty_value(self):
        opts = parse(CustomParseOptions, ["--pair", "key:"])
        assert opts.pair == ("key", "")
