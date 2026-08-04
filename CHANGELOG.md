# Changelog

## [1.0.0](https://github.com/koesterlab/ddargparse/compare/v0.3.2...v1.0.0) (2026-08-04)


### ⚠ BREAKING CHANGES

* rename public method parse_args into from_cli_args and from_cli_args into from_parsed_cli_args (attention, this will break your code, sorry!) ([#13](https://github.com/koesterlab/ddargparse/issues/13))

### Features

* move field interpretation into separate class ([#11](https://github.com/koesterlab/ddargparse/issues/11)) ([f29fb39](https://github.com/koesterlab/ddargparse/commit/f29fb39146c70252706fcd0ec0e7995b223c8811))


### Bug Fixes

* fix handling of nested subcommand dataclasses and add corresponding tests ([#14](https://github.com/koesterlab/ddargparse/issues/14)) ([fc552eb](https://github.com/koesterlab/ddargparse/commit/fc552eb54d48ec15a63f01aa2353fab6ca4394d6))


### Code Refactoring

* rename public method parse_args into from_cli_args and from_cli_args into from_parsed_cli_args (attention, this will break your code, sorry!) ([#13](https://github.com/koesterlab/ddargparse/issues/13)) ([b916b86](https://github.com/koesterlab/ddargparse/commit/b916b86625f9186f5fa103ad3dbe21a2d7cb0aad))

## [0.3.2](https://github.com/koesterlab/ddargparse/compare/v0.3.1...v0.3.2) (2026-03-21)


### Bug Fixes

* parse_args taking only optional parameters now ([7c6d371](https://github.com/koesterlab/ddargparse/commit/7c6d3715303986a031d0e6931907887db3bfe2e6))

## [0.3.1](https://github.com/koesterlab/ddargparse/compare/v0.3.0...v0.3.1) (2026-03-21)


### Bug Fixes

* improve compat with older python versions and fix parse_args signature ([0dd6e29](https://github.com/koesterlab/ddargparse/commit/0dd6e29e3a7bfcfbb8df5cd168ee7027f92e0681))

## [0.3.0](https://github.com/koesterlab/ddargparse/compare/v0.2.0...v0.3.0) (2026-03-21)


### Features

* dataclass-only mode ([#7](https://github.com/koesterlab/ddargparse/issues/7)) ([f1808b2](https://github.com/koesterlab/ddargparse/commit/f1808b262a90432de10b173dc9bfc0d619980474))
* proper handling of Enum types ([7cb3bc6](https://github.com/koesterlab/ddargparse/commit/7cb3bc6a6e778035a494c697d658d5fafa5e8426))

## [0.2.0](https://github.com/koesterlab/ddargparse/compare/v0.1.4...v0.2.0) (2026-03-20)


### Features

* add ability to choose between append-style (`--arg item1 --arg item2 --arg item3`) and nargs-style (default, `--arg item1 item2 item3`) list arguments via `register_cli_args(..., list_append=True|False)` ([0484663](https://github.com/koesterlab/ddargparse/commit/048466323be5dd9195f9e13c1c59b53dce876f05))


### Documentation

* more structured usage ([366d34d](https://github.com/koesterlab/ddargparse/commit/366d34dccaffbea111280984d5715076f3a2530f))
* polish readme ([265fcff](https://github.com/koesterlab/ddargparse/commit/265fcff2c4ecb164bdcbb24357a420ca0054556d))

## [0.1.4](https://github.com/koesterlab/ddargparse/compare/v0.1.3...v0.1.4) (2026-03-20)


### Documentation

* more examples ([4079f3e](https://github.com/koesterlab/ddargparse/commit/4079f3e31a467434f36ea83f655ff20355d2345e))

## [0.1.3](https://github.com/koesterlab/ddargparse/compare/v0.1.2...v0.1.3) (2026-03-20)


### Bug Fixes

* do not use pixi cache ([8ed8f83](https://github.com/koesterlab/ddargparse/commit/8ed8f839ca1dbb96418924cb248c4596932b8e02))

## [0.1.2](https://github.com/koesterlab/ddargparse/compare/v0.1.1...v0.1.2) (2026-03-20)


### Bug Fixes

* setup trusted publishing ([d5d877d](https://github.com/koesterlab/ddargparse/commit/d5d877d2def62407eb4e14bba07d4d5d4875357b))

## [0.1.1](https://github.com/koesterlab/ddargparse/compare/v0.1.0...v0.1.1) (2026-03-20)


### Documentation

* add license ([a10fd91](https://github.com/koesterlab/ddargparse/commit/a10fd917e55b847a7776987a2fa560685fe8f92d))
