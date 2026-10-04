# logtool

A CLI tool for analyzing JSON-per-line logs.

## Usage

    python logtool.py <path> [--show-reasons] [--json]

## Examples

    python logtool.py sample.log
    python logtool.py sample_broken.log --show-reasons
    python logtool.py sample.log --json

## What it does

- Parses JSON-per-line log files
- Counts log levels (INFO/WARN/ERROR) and services
- Gracefully skips malformed lines and reports why
- Handles missing files without crashing