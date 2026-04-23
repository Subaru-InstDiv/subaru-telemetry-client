# Agent Instructions — subaru-telemetry-client

## Ecosystem context

This repository is the **Python client library** for the Subaru Telemetry System (STS). It is used
as a dependency by sensor polling scripts in the companion repositories:

- [`subaru-telemetry-server`](https://github.com/Subaru-InstDiv/subaru-telemetry-server) — STSboard
  daemon, radio server, alarm subsystem, and all sensor polling scripts
- [`subaru-telemetry-web`](https://github.com/Subaru-InstDiv/subaru-telemetry-web) — Flask web
  frontend for telemetry dashboards

This library encodes the **STS binary wire protocol**. Any change to `Radio.pack` or `Radio.unpack`
affects every sensor script in the ecosystem and must be treated with extreme care.

---

## Commands

```bash
uv sync                                                     # install / refresh the environment
uv run pytest                                               # run all tests (may attempt network I/O)
uv run pytest -k 'not transmit_method and not receive_method'  # unit tests only (no network)
uv run ruff format .                                        # format code
uv run ruff check . --fix                                   # lint and auto-fix
```

Coverage must stay at or above **80 %**. The CI gate will fail below this threshold.

---

## Git workflow

**Never commit directly to `main`.** All changes must go through a feature branch and pull request.

```sh
git checkout main && git pull          # start from a fresh main
git checkout -b <type>/<description>   # create a feature branch
# ... make changes ...
git push -u origin <branch-name>
gh pr create --base main
```

Branch names follow `<type>/<short-description>` in lowercase kebab-case:

| Type | When to use |
|---|---|
| `feat/` | new public API, new datum format support |
| `fix/` | bug fix |
| `chore/` | dependency updates, config changes |
| `docs/` | README or documentation only |
| `refactor/` | internal restructuring with no behaviour change |
| `test/` | adding or improving tests |

Examples: `feat/add-datum-batch-helper`, `fix/radio-recv-timeout`, `chore/bump-ruff`

### Commit message format

```
feat: add FloatArray datum format
fix: handle partial recv in _recvn
chore: upgrade ruff to 0.9.0
```

Keep the subject line under 72 characters. Add a blank line and body if the change is non-obvious.

---

## Architecture

### `Datum` — `src/subaru/sts/client/datum.py`

A lightweight, immutable-by-convention value container. Instances are created via factory class
methods:

| Factory method | Format constant | Python value type |
|---|---|---|
| `Datum.Integer(id, timestamp, value)` | `INTEGER` | `int` |
| `Datum.Float(id, timestamp, value)` | `FLOAT` | `int \| float` |
| `Datum.Text(id, timestamp, value)` | `TEXT` | `str` |
| `Datum.IntegerWithText(id, timestamp, value)` | `INTEGER_WITH_TEXT` | `tuple[int, str]` |
| `Datum.FloatWithText(id, timestamp, value)` | `FLOAT_WITH_TEXT` | `tuple[float, str]` |
| `Datum.Exponent(id, timestamp, value)` | `EXPONENT` | `int \| float` |

`EXPONENT` is identical to `FLOAT` on the wire; the distinction is presentational (the STS web
frontend may render it in scientific notation).

The constructor validates that the value type matches the declared format and raises `ValueError`
on mismatch.

### `Radio` — `src/subaru/sts/client/radio.py`

The TCP client. Connects to the STS board (default `host="sts"`, `port=9001`), speaks the binary
protocol, and exposes two public methods:

- `radio.transmit(data)` — sends a list of `Datum` objects
- `radio.receive(ids)` — fetches the latest `Datum` for each ID in `ids`

Pass `dry_run=True` to the constructor (or to `transmit()`) to exercise packing without touching
the network — useful for sensor script development and unit tests.

### Binary protocol

Each packet is a `bytearray` with the structure:

```
Header  (10 bytes):  !BIBI  →  size | 0x80, datum_id, format, timestamp
Payload (variable):  format-specific (integer = 4 B, float/exponent = 8 B, text = up to 117 B)
```

Maximum packet size is 127 bytes. Text payloads are silently truncated to fit.

---

## Code conventions

- **Python ≥ 3.12** everywhere.
- **Absolute imports** starting from `subaru` (e.g. `from subaru.sts.client import Datum, Radio`).
- **Numpy-style docstrings** on all public classes, methods, and functions.
- **Ruff** for formatting and linting — configuration lives in `pyproject.toml`. Line length 100.
- Do not add logging frameworks. This is a library; callers control their own logging.
- Do not introduce runtime dependencies. The library intentionally has no `dependencies` in
  `pyproject.toml` beyond the Python standard library.

---

## Testing

Tests live in `tests/`. Two categories:

- **Unit tests** — test packing/unpacking, factory methods, and validation logic with no network.
  These can always run offline.
- **Integration tests** — `test_radio.py` methods tagged `transmit_method` and `receive_method`
  open a real TCP connection to the STS board. Skip these when working offline:
  ```bash
  uv run pytest -k 'not transmit_method and not receive_method'
  ```

When adding a new datum format or changing pack/unpack logic, add a round-trip test that packs a
`Datum` and immediately unpacks the result, verifying the values are identical.

Test files in `tests/` may omit module-level and function-level docstrings (`D100`, `D103` are
ignored there by ruff).

---

## Adding a new datum format

If the STS board protocol is extended to support a new format:

1. Add the new constant to `DatumFormat` in `datum.py`.
2. Add a factory class method on `Datum`.
3. Add value validation in `Datum._validate_value`.
4. Add `pack` and `unpack` branches in `Radio.pack` / `Radio.unpack`.
5. Add unit tests covering the factory method, validation, pack, and unpack.
6. Update `README.md` with the new factory method and value type.

---

## What NOT to do

- Do not commit directly to `main`.
- Do not add third-party runtime dependencies.
- Do not change `Radio.pack` or `Radio.unpack` without adding or updating round-trip tests.
- Do not lower the 80 % coverage threshold.
- Do not hard-code machine-specific paths (e.g., absolute paths to `uv`) in source code or tests.
- Do not use relative imports — all imports must start from `subaru`.
