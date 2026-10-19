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