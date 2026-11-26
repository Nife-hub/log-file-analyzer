from func import parse_log_line

def test_func():
    line = "2026-11-05 14:20:10 WARNING"
    result = parse_log_line(line)
    assert result is None, 'Invalid log'