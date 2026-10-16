import pytest

from backend.admin_parse import parse_limit
from backend.units import format_mb, parse_size_mb


def test_sizes_parse_and_format():
    assert parse_size_mb("2g") == 2048 and parse_size_mb("512m") == 512 and parse_size_mb("1.5T") == 1.5 * 1024 * 1024
    assert format_mb(2048) == "2.0G" and format_mb(300) == "300M"
    for bad in ("0", "abc", "-1g", ""):
        with pytest.raises(ValueError):
            parse_size_mb(bad)


def test_limit_values_and_reset():
    assert parse_limit("mem_mb", "1g") == 1024 and parse_limit("cpu", "0.5") == 0.5 and parse_limit("procs", "100") == 100.0
    assert parse_limit("disk_mb", "default") is None
    with pytest.raises(ValueError):
        parse_limit("cpu", "0")
