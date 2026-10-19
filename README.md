# logtool

![Tests](https://github.com/Kharageous/logtool/actions/workflows/tests.yml/badge.svg)

A CLI tool for analyzing JSON-per-line logs. It counts log levels and services,
gracefully skips malformed lines, and reports exactly what it found — built for
the messy reality of production log files.

## Why

Structured logs (JSON-per-line) are the standard in modern infrastructure — Ray,
vLLM, PyTorch Lightning, and most cloud services emit them. But `grep` and `awk`
don't understand JSON, and dumping a 10 GB file into a Python REPL is not a plan.

`logtool` is a small, dependency-free tool that answers the first questions you
ask during an incident:

- How many `ERROR` lines are in this log?
- Which service is logging the most?
- How many lines are corrupt, and why?
- What are the top 2 noisiest levels?

## Features

- Parses JSON-per-line log files line by line (constant memory — handles huge files)
- Counts log levels (`INFO`, `WARN`, `ERROR`, …) and services
- Gracefully skips malformed lines and reports the reason for each skip
- Handles missing files and permission errors without crashing
- `--top N` — show only the busiest N levels and services
- `--json` — machine-readable output for piping into other tools
- `--show-reasons` — explain exactly why lines were skipped
- Zero external dependencies (standard library only)
- 8 automated tests, run on every push via GitHub Actions

## Installation

Requires **Python 3.10 or later**.

```bash
git clone git@github.com:Kharageous/logtool.git
cd logtool
```

No `pip install` needed — `logtool` uses only the Python standard library.

To run the tests, install `pytest`:

```bash
pip install pytest
# or, on Debian/Ubuntu:
sudo apt install python3-pytest
```

## Usage

```bash
python3 logtool.py <path> [--show-reasons] [--json] [--top N]
```

### Options

| Flag | Description |
|------|-------------|
| `path` | Path to the JSON-per-line log file to analyze (required) |
| `--show-reasons` | Show why lines were skipped |
| `--json` | Output raw JSON instead of formatted text |
| `--top N` | Show only the top N entries (levels and services) |

### Examples

**Basic analysis** — counts by level and service:

```bash
python3 logtool.py sample.log
```

Output:

```
Levels:   {'INFO': 3, 'ERROR': 3, 'WARN': 1}
Services: {'trainer': 4, 'dataloader': 2, 'checkpoint': 1}
Skipped:  0
```

**Handle malformed logs** — see why lines were skipped:

```bash
python3 logtool.py sample_broken.log --show-reasons
```

Output:

```
Levels:   {'INFO': 2, 'ERROR': 1}
Services: {'trainer': 3}
Skipped:  2
Reasons:
  bad json: 1
  missing key 'level': 1
```

**Top N** — only the busiest entries:

```bash
python3 logtool.py sample.log --top 2
```

Output:

```
Levels:   {'INFO': 3, 'ERROR': 3}
Services: {'trainer': 4, 'dataloader': 2}
Skipped:  0
```

**Machine-readable output** — pipe into `jq` or another tool:

```bash
python3 logtool.py sample.log --json
```

```json
{
  "levels": {
    "INFO": 3,
    "ERROR": 3,
    "WARN": 1
  },
  "services": {
    "trainer": 4,
    "dataloader": 2,
    "checkpoint": 1
  },
  "skipped": 0,
  "reasons": {}
}
```

**Combine flags** — JSON output that includes skip reasons:

```bash
python3 logtool.py sample_broken.log --json --show-reasons
```

## Input format

Each line of the log file must be a JSON object with at least these fields:

```json
{"ts": "2024-01-01T10:00:00", "level": "INFO", "service": "trainer", "msg": "epoch 1 started"}
```

| Field | Required | Purpose |
|-------|----------|---------|
| `level` | Yes | Counted in the level summary |
| `service` | Yes | Counted in the service summary |
| `ts`, `msg` | No | Ignored by `logtool`, but usually present |

Lines that are not valid JSON, or that are missing `level` or `service`, are
counted as **skipped** and do not crash the tool.

## Testing

```bash
pytest -v
```

The suite has **8 tests** covering:

- Level and service counting on valid input
- Skip handling for malformed JSON
- Skip handling for missing required keys
- Missing-file behavior (returns `None`, no traceback)
- `--top N` truncation (correct count and correct winners)
- `--top N` when `N` is larger than the number of entries
- Return type and structure validation

CI runs the full suite on every push and pull request to `main` via
[GitHub Actions](.github/workflows/tests.yml). The badge at the top of this README
reflects the latest run.

## Project structure

```
logtool/
├── logtool.py                  # The CLI tool (analyze + print_report + main)
├── test_logtool.py             # pytest test suite (8 tests)
├── sample.log                  # Sample valid log file
├── sample_broken.log           # Sample log with 2 malformed lines
├── README.md                   # This file
├── .gitignore                  # Python artifacts, virtualenvs, .env
└── .github/
    └── workflows/
        └── tests.yml           # GitHub Actions CI config
```

## How it works

1. `main()` parses arguments with `argparse`.
2. `analyze(path)` opens the file with `with open(...)`, iterates line by line,
   and for each line:
   - calls `json.loads()`,
   - increments `level_counter` and `service_counter` (both `defaultdict(int)`),
   - catches `json.JSONDecodeError` and `KeyError` separately, recording the
     reason in `skipped_reasons`.
3. `print_report(result, show_reasons, top_n)` formats the result, optionally
   sorting by count descending and truncating to `top_n`.
4. If `--json` is given, `print_report` is skipped and the raw `result` dict is
   dumped with `json.dumps(result, indent=2)`.

The whole tool is roughly 80 lines of Python. It is intentionally small so it
can be read in one sitting.

## Design notes

- **Constant memory.** The file is iterated line by line, never read into memory
  as a whole. A 50 GB log file uses the same RAM as a 50 KB one.
- **Fail soft on bad data, hard on bad input.** A malformed log line is skipped
  and counted. A missing file or a non-directory argument exits with a clear
  error and a non-zero status.
- **stderr for errors, stdout for data.** Error messages go to `sys.stderr` so
  that `python3 logtool.py app.log > report.txt` still produces a clean report
  file even when the tool hits a problem.
- **Zero dependencies.** No `pip install` required to run the tool — the standard
  library is enough.

## License

MIT — see [LICENSE](LICENSE) for details.

## Contributing

Issues and pull requests are welcome. Please run `pytest -v` before opening a PR
— CI will also run the suite automatically.
```
