from devops_utils import get_system_info, check_health, format_bytes


def test_system_info_returns_dict():
    result = get_system_info()
    assert isinstance(result, dict)
    assert "hostname" in result
    assert "python_version" in result


def test_check_health_valid():
    result = check_health("nginx")
    assert result["status"] == "healthy"
    assert result["service"] == "nginx"


def test_check_health_invalid():
    result = check_health("")
    assert result["status"] == "error"


def test_format_bytes_kb():
    assert "KB" in format_bytes(1024)


def test_format_bytes_mb():
    assert "MB" in format_bytes(1024 * 1024)


def test_format_bytes_gb():
    assert "GB" in format_bytes(1024 * 1024 * 1024)
