# STSpy

[![Tests](https://github.com/Subaru-InstDiv/subaru-sts-client/actions/workflows/python-tests.yml/badge.svg)](https://github.com/Subaru-InstDiv/sts-client/actions/workflows/python-tests.yml)
[![codecov](https://codecov.io/gh/Subaru-InstDiv/subaru-sts-client/branch/main/graph/badge.svg)](https://codecov.io/gh/Subaru-InstDiv/subaru-sts-client)

## Overview

- `subaru-sts-client` is a small Python library for communicating with the Subaru Telescope STS board ("STS radio").
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

Package name (when published): `subaru-sts-client`.

- Install from source (in this repository's root):
    - `python -m pip install .`
- Editable/development install:
    - `python -m pip install -e .`
- Development install with dev tools:
    - `python -m pip install -e ".[dev]"`

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
radio = Radio() 
radio.transmit([d1, d2, d3, d4, d5, d6])

# Get the lastest values by id.
latest = radio.receive([1090, 1091, 1092, 1093, 1094, 1095])
print(latest)
```

## Configuration

- Radio defaults (as defined in src/subaru/sts/client/radio.py):
    - HOST: `sts`
    - PORT: `9001`
    - TIMEOUT: `5.0` seconds
- You can override these via the constructor:
    - `Radio(host='example.org', port=9001, timeout=2.0)`

## Tests

- Some tests are pure unit tests (packing/unpacking, factory methods), and others perform live network I/O against the
  default STS HOST/PORT.
- Running all tests as-is may attempt to connect to sts:9001 and may fail or hang if not reachable.

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
