<!--
SPDX-FileCopyrightText: Fondation RERO+
SPDX-License-Identifier: BSD-3-Clause
-->

# Changelog

<!-- version list -->

## v4.1.0 (2026-09-07)

### Features

- Serve one value of the variable prefix without naming it
  ([`90c7373`](https://github.com/rero/flask-wiki/commit/90c73738edfbfdc7af19796aa58344baec37861c))


## v4.0.0 (2026-09-04)

### Bug Fixes

- Repair the page lookups that never ran
  ([`d24dc56`](https://github.com/rero/flask-wiki/commit/d24dc567ef746809cd74a015eeb656f52767bfa1))

- Scope the JS handlers to what was clicked, and tidy the rest
  ([`b791f93`](https://github.com/rero/flask-wiki/commit/b791f936942edabf3af3820395395b6653c5823a))

### Chores

- **i18n**: Translate the preview messages and refresh catalogs
  ([`e78a8d7`](https://github.com/rero/flask-wiki/commit/e78a8d7b1cea6cb9830f98d720af9a2400fcf54f))

### Features

- Let WIKI_URL_PREFIX carry a variable part
  ([`15df243`](https://github.com/rero/flask-wiki/commit/15df243f5873bbd775c6922b42edf72bf65334d8))

- Make the toast markup swappable, like the icons
  ([`6af5d9b`](https://github.com/rero/flask-wiki/commit/6af5d9bf35f9c9d21b2564a10b99225bbefa42fb))

- One grid and one toast stack for every page
  ([`1a8fc03`](https://github.com/rero/flask-wiki/commit/1a8fc03a4fd63693154c299cde8e8344a74fc400))

- Render captioned figures and own toast placement
  ([`eb65df1`](https://github.com/rero/flask-wiki/commit/eb65df15b56483884803057c4e0fa0574764bab0))


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
