# STSpy

[![Tests](https://github.com/Subaru-InstDiv/subaru-telemetry-client/actions/workflows/python-tests.yml/badge.svg)](https://github.com/Subaru-InstDiv/subaru-telemetry-client/actions/workflows/python-tests.yml)
[![codecov](https://codecov.io/gh/Subaru-InstDiv/subaru-telemetry-client/branch/main/graph/badge.svg)](https://codecov.io/gh/Subaru-InstDiv/subaru-telemetry-client)


## Ecosystem

This library is one part of the Subaru Telemetry System (STS):

| Repository | Role |
|---|---|
| **subaru-telemetry-client** *(this repo)* | Python client library — packs/unpacks the STS binary protocol and transmits/receives datum values over TCP |
| [`subaru-telemetry-server`](https://github.com/Subaru-InstDiv/subaru-telemetry-server) | STSboard daemon, radio server, alarm subsystem, and all sensor polling scripts |
| [`subaru-telemetry-web`](https://github.com/Subaru-InstDiv/subaru-telemetry-web) | Flask web frontend for telemetry dashboards |

Sensor scripts in `subaru-telemetry-server` declare this library as a dependency and import
`Datum` and `Radio` from it.

---

## Overview

- `subaru-telemetry-client` is a small Python library for communicating with the Subaru Telescope STS board ("STS radio").
- It provides two core classes:
    - `subaru.sts.client.dataum.Datum`: a lightweight container representing typed values (integer, float, text,
      integer-with-text, float-with-text, exponent) with an STS radio ID and timestamp.
    - `subaru.sts.client.radio.Radio`: a client that packs/unpacks STS binary protocol messages and transmits/receives
      data to/from an STS board over TCP.

## Requirements

- Python 3.12+.
- Network access to an STS board if you intend to run the integration tests or use Radio.transmit/Radio.receive against
  a live system.

## Installation

This is an internal library. Install directly from the repository using `git+ssh`. By default, you should use the latest version:

- **Standard Installation:**
  ```bash
  pip install "git+ssh://git@github.com/Subaru-InstDiv/subaru-telemetry-client.git"
  ```

- **Specifying a Version (Optional):**
  If you need to pin to a specific version, you can append a tag (e.g., `@v1.0.0`):
  ```bash
  pip install "git+ssh://git@github.com/Subaru-InstDiv/subaru-telemetry-client.git@v1.0.0"
  ```

- **For Development (editable):**
  Clone the repository and install in editable mode:
  ```bash
  git clone git@github.com:Subaru-InstDiv/subaru-telemetry-client.git
  cd subaru-telemetry-client
  uv sync --extra dev
  ```

## Usage

Once installed, import as shown below. You can also use the package directly from the source tree by running Python from the repository root (src/ layout is discovered automatically by setuptools-installed packages).

## Quick start examples

```py
import time
from subaru.sts.client import Radio, Datum

now = int(time.time())

# Create some Datum instances.
d1 = Datum.Integer(id=1090, timestamp=now, value=1)
d2 = Datum.Float(id=1091, timestamp=now, value=3.14)
d3 = Datum.Text(id=1092, timestamp=now, value='hello')
d4 = Datum.IntegerWithText(id=1093, timestamp=now, value=(1, 'ok'))
d5 = Datum.FloatWithText(id=1094, timestamp=now, value=(2.5, 'm/s'))
d6 = Datum.Exponent(id=1095, timestamp=now, value=1.0)

# Create a radio to broadcast/receive data.
# Pass host="sts" (or your server hostname) to connect to production.
radio = Radio()
radio.transmit([d1, d2, d3, d4, d5, d6])

# Get the lastest values by id.
latest = radio.receive([1090, 1091, 1092, 1093, 1094, 1095])
print(latest)
```

## Configuration

- Radio defaults (as defined in src/subaru/sts/client/radio.py):
    - HOST: `localhost`
    - PORT: `9001`
    - TIMEOUT: `5.0` seconds
    - `dry_run`: `False` (constructor parameter; no class constant)
- You can override these via the constructor:
    - `Radio(host='example.org', port=9001, timeout=2.0, dry_run=True)`
- You can also override `dry_run` for individual transmit calls:
    - `radio.transmit(data, dry_run=True)`

## Internal datums — connectivity and smoke-testing

The STS board always pre-seeds three datum IDs at startup that do not correspond to any physical sensor. They exist **in-memory only** — they are not rows in the MySQL `datum` table, so writes to them are not archived.

| Datum ID | Name | Format | Notes |
|---|---|---|---|
| `0` | STSboard CPU Load | `Float` | Overwritten every 5 s by the board; client writes are accepted but immediately superseded |
| `1` | STSboard Test1 | `IntegerWithText` | Writable; no alarm, no archival side-effects; persists in memory until board restarts |
| `2` | STSboard Test2 | `FloatWithText` | Writable; no alarm, no archival side-effects; persists in memory until board restarts |

Datum IDs 1 and 2 are the recommended targets for connectivity checks and smoke tests. Writes succeed at the protocol level and are immediately readable back via `receive()`.

> **Format note:** The format byte in the transmitted packet determines how the value is stored. Pass the correct datum type — `IntegerWithText` for ID 1, `FloatWithText` for ID 2 — to ensure `receive()` returns the expected Python type.

> **MySQL note:** Because these datums are not in the `datum` table, the bridge will log (and discard) a MySQL write error for each update. This is harmless and does not affect in-memory reads.

### Connectivity check example

```python
import time
from subaru.sts.client import Radio, Datum

radio = Radio()  # defaults to localhost:9001; pass host='sts' for production

# Read the board's CPU load — always available, no write needed
cpu = radio.receive([0])
print('Board CPU load:', cpu[0].value)

# Round-trip a write+read on the safe test datum
now = int(time.time())
radio.transmit([Datum.IntegerWithText(id=1, timestamp=now, value=(42, 'ok'))])
result = radio.receive([1])
assert result[0].value == (42, 'ok'), f"unexpected: {result[0].value}"
print('Round-trip OK')
```

## Tests

- Some tests are pure unit tests (packing/unpacking, factory methods), and others perform live network I/O against the
  default STS HOST/PORT.
- Running all tests as-is may attempt to connect to localhost:9001 and may fail or hang if no local STS server is running.

### Run tests

- Run all tests (may attempt network access):
    - `uv run pytest -v`
- Run only offline/unit tests (examples):
    - `uv run pytest -v -k 'not transmit_method and not receive_method'`

### Code quality and formatting

- This project uses `ruff` for both linting and code formatting.
- Ruff configuration is defined in `pyproject.toml` and follows:
    - Line length: 100 characters
    - Target: Python 3.12
    - Docstring convention: numpy

#### Code quality commands with UV:

- Format code:
    - `uv run ruff format .`
- Check formatting without changes:
    - `uv run ruff format --check .`
- Lint code:
    - `uv run ruff check .`
- Lint and auto-fix issues:
    - `uv run ruff check --fix .`
- Run all quality checks (lint + format check):
    - `uv run ruff check . && uv run ruff format --check .`

- If you wish to run integration tests that hit the live STS server, ensure network connectivity and that the HOST/PORT
  are correct or pass custom values when constructing Radio in your own tests.

## Development notes

- Network protocol: The Radio class uses struct to pack/unpack a specific binary protocol header and payload for STS.
  See radio.py for details.

## Known limitations

- Integration tests depend on external network availability and an accessible STS board.
