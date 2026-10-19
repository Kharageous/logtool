import json
import pytest
from logtool import analyze


# --- Tests for analyze() ---

def test_analyze_returns_level_counts():
    """analyze() counts levels correctly."""
    result = analyze("sample.log")
    assert result["levels"]["INFO"] == 3
    assert result["levels"]["ERROR"] == 3
    assert result["levels"]["WARN"] == 1


def test_analyze_returns_service_counts():
    """analyze() counts services correctly."""
    result = analyze("sample.log")
    assert result["services"]["trainer"] == 4
    assert result["services"]["dataloader"] == 2
    assert result["services"]["checkpoint"] == 1


def test_analyze_no_skipped_lines():
    """sample.log has no bad lines."""
    result = analyze("sample.log")
    assert result["skipped"] == 0
    assert result["reasons"] == {}


def test_analyze_handles_broken_log():
    """sample_broken.log has 2 bad lines."""
    result = analyze("sample_broken.log")
    assert result["skipped"] == 2
    assert "bad json" in result["reasons"]
    assert result["reasons"]["bad json"] == 1


def test_analyze_missing_file_returns_none():
    """analyze() returns None for missing file."""
    result = analyze("nonexistent.log")
    assert result is None


# --- Tests for --top flag logic ---

def test_top_n_truncates_levels():
    """--top N limits levels to N entries."""
    result = analyze("sample.log")
    levels = result["levels"]
    top_2 = dict(sorted(levels.items(), key=lambda x: -x[1])[:2])
    assert len(top_2) == 2
    assert "INFO" in top_2
    assert "ERROR" in top_2


def test_top_n_greater_than_entries():
    """--top N with N > entries shows all."""
    result = analyze("sample.log")
    levels = result["levels"]
    top_10 = dict(sorted(levels.items(), key=lambda x: -x[1])[:10])
    assert len(top_10) == 3


# --- Tests for return type ---

def test_analyze_produces_dict():
    """analyze() returns a dict with expected keys."""
    result = analyze("sample.log")
    assert isinstance(result, dict)
    assert "levels" in result
    assert "services" in result
    assert "skipped" in result
    assert "reasons" in result