<!--
SPDX-FileCopyrightText: Fondation RERO+
SPDX-License-Identifier: BSD-3-Clause
-->

# Changelog

<!-- version list -->

## v3.0.0 (2026-09-03)

### Bug Fixes

- Handle legacy pages in move and language fallback
  ([`3273fe1`](https://github.com/rero/flask-wiki/commit/3273fe1b0146d453ecc8ea10ac23239f3113803e))

- Index pages that contain wikilinks
  ([`73ac1f0`](https://github.com/rero/flask-wiki/commit/73ac1f0fde5cb76045df4368fed934f03d96da8d))

### Build System

- Add semantic release shortcut commands
  ([`3e3cac8`](https://github.com/rero/flask-wiki/commit/3e3cac8054ffa561bc458f9c6df50ed6345b7d20))

- Update dependencies
  ([`20daad6`](https://github.com/rero/flask-wiki/commit/20daad63112d255139c8e5220b5eebfadfd4df93))

- **deps**: Run python-semantic-release through uvx
  ([`2d8795a`](https://github.com/rero/flask-wiki/commit/2d8795a167e8a208b255e9cd9548a668c575f329))

### Chores

- Adopt SPDX license headers and drop Python 3.10/3.11
  ([`3136f15`](https://github.com/rero/flask-wiki/commit/3136f1551a174bad5aac26ec1843cc674edee37f))

- Update dependencies and clean up CLAUDE.md
  ([`afd755e`](https://github.com/rero/flask-wiki/commit/afd755e3ab995774fd4fc768b56678a3f96310dd))

- **i18n**: Refresh catalogs and fix broken translations
  ([`d66071c`](https://github.com/rero/flask-wiki/commit/d66071cfc7f2fea382e97f0fba4cf876fc2973b7))

### Continuous Integration

- Add automatic release publication and repo automation
  ([`a44ddc3`](https://github.com/rero/flask-wiki/commit/a44ddc3ff6c0077ab8eb4a0f5d2fba4076abf101))

### Documentation

- Add missing docstrings
  ([`94a36e2`](https://github.com/rero/flask-wiki/commit/94a36e2f2d3b3ef3404ced1ebb8b78b574089298))

- Correct the supported Python version
  ([`029d9b1`](https://github.com/rero/flask-wiki/commit/029d9b1968eabd3cd0eb3135a94d86d15a1dd416))

- Rework the example wiki into a multilingual demo
  ([`04fefdc`](https://github.com/rero/flask-wiki/commit/04fefdcf515cd347f8af6a0cb74cdae5e1c7309d))

### Features

- Drop Font Awesome for the Bootstrap Icons sprite
  ([`24c4884`](https://github.com/rero/flask-wiki/commit/24c488499a3ec110338a9acfa0199bd325e7785d))

- Make the icon set swappable with WIKI_ICON_TEMPLATE
  ([`5ef7e6d`](https://github.com/rero/flask-wiki/commit/5ef7e6d1a001e2bb8fd7d46175255ca718ca29b9))

- Remove EasyMDE and edit pages in a plain textarea
  ([`4c1ab78`](https://github.com/rero/flask-wiki/commit/4c1ab78ed64596260f855896065af69f7b7a7af5))

- Serve missing translations in a fallback language
  ([`dba5f3b`](https://github.com/rero/flask-wiki/commit/dba5f3bd62f70c08716f5341294460df4e43561b))

- Show which language is being edited
  ([`8840a48`](https://github.com/rero/flask-wiki/commit/8840a48047b19c2176941c170cc58b86ed0a7394))

### Refactoring

- Make the footer credit translatable
  ([`306b99d`](https://github.com/rero/flask-wiki/commit/306b99d0affbc001946ef361180ecf4d790f4e8b))


## [v2.0.0](https://github.com/rero/flask-wiki/tree/v2.0.0) (2026-03-26)

[Full Changelog](https://github.com/rero/flask-wiki/compare/v1.0.4...v2.0.0)

- BREAKING CHANGE: deprecates Python<3.10.
- feat: add basic test suite [\#80](https://github.com/rero/flask-wiki/pull/80) (by @PascalRepond)
- chore: update dependencies [\#79](https://github.com/rero/flask-wiki/pull/79) (by @PascalRepond)

## [v1.0.4](https://github.com/rero/flask-wiki/tree/v1.0.4) (2025-12-10)

[Full Changelog](https://github.com/rero/flask-wiki/compare/v1.0.3...v1.0.4)

- chore: update dependencies [\#77](https://github.com/rero/flask-wiki/pull/77) (by @PascalRepond)
- chore(actions): auto-assign PR author (by @PascalRepond)

## [v1.0.3](https://github.com/rero/flask-wiki/tree/v1.0.3) (2025-08-05)

[Full Changelog](https://github.com/rero/flask-wiki/compare/v1.0.2...v1.0.3)

- chore: use uv_publish as a build system (by @PascalRepond)

## [v1.0.2](https://github.com/rero/flask-wiki/tree/v1.0.2) (2025-07-31)

**Changes:**

- feat(dev): add uv and ruff [\#72](https://github.com/rero/flask-wiki/pull/72) (by @PascalRepond)

## [v1.0.1](https://github.com/rero/flask-wiki/tree/v1.0.1) (2025-05-15)

[Full Changelog](https://github.com/rero/flask-wiki/compare/v1.0.0...v1.0.1)

**Fix:**

- Unlock wtforms version (by @rerowep & @PascalRepond)

## [v1.0.0](https://github.com/rero/flask-wiki/tree/v1.0.0) (2025-05-15)

[Full Changelog](https://github.com/rero/flask-wiki/compare/v0.3.1...v1.0.0)

**Fixes:**

- edit typo in README.md [\#67](https://github.com/rero/flask-wiki/pull/67) (by @putassu)

**Other changes:**

- chore(actions): pypi publish package using poetry [\#71](https://github.com/rero/flask-wiki/pull/71) (by @PascalRepond)
- project: update dependencies [\#70](https://github.com/rero/flask-wiki/pull/70) (by @rerowep)
- chore: update dependencies [\#69](https://github.com/rero/flask-wiki/pull/69) (by @PascalRepond)

## [v0.3.1](https://github.com/rero/flask-wiki/tree/v0.3.0) (2023-12-13)

[Full Changelog](https://github.com/rero/flask-wiki/compare/v0.3.0...v0.3.1)

**Fixes:**

- fix: config languages [\#65](https://github.com/rero/flask-wiki/pull/65) (by @PascalRepond)

## [v0.3.0](https://github.com/rero/flask-wiki/tree/v0.3.0) (2023-08-24)

[Full Changelog](https://github.com/rero/flask-wiki/compare/v0.2.4...v0.3.0)

**New features:**

- search: implement whoosh search engine [\#63](https://github.com/rero/flask-wiki/pull/63) (by @PascalRepond)

**Fixes:**

- translations: fix flask-babel compatibility [\#62](https://github.com/rero/flask-wiki/pull/62) (by @PascalRepond)
- chore: add pytest and fix styling errors [\#61](https://github.com/rero/flask-wiki/pull/61) (by @PascalRepond)
- project: update dependencies [\#59](https://github.com/rero/flask-wiki/pull/59) (by @rerowep)
