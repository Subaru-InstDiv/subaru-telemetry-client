# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added

- **Internal datums connectivity section** in `README.md`: Documents the three always-present datum IDs (0 = CPU load, 1 = Test1, 2 = Test2) that are pre-seeded by the Go `sts-board` daemon at startup. Includes a Python connectivity-check example using `Radio.receive` and `Radio.transmit` against these safe test targets.

### Changed
- `Radio` default `host` changed from `"sts"` (the production server hostname) to `"localhost"` for safety. Scripts targeting the production STS board must now pass `host="sts"` explicitly.
