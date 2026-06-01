# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Changed
- `Radio` default `host` changed from `"sts"` (the production server hostname) to `"localhost"` for safety. Scripts targeting the production STS board must now pass `host="sts"` explicitly.
