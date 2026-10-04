import pytest

from src.core.sandbox import Denied, SandboxedCaps


def test_declared_permission_lets_action_through():
    sink: list[tuple[str, str]] = []
    caps = SandboxedCaps(["fs:report.csv"], sink)

    ref = caps.fs_write("report.csv", "e1;echo")

    assert ref == "file-1"
    assert sink == [("fs:report.csv", "e1;echo")]


def test_undeclared_permission_is_denied():
    sink: list[tuple[str, str]] = []
    caps = SandboxedCaps(["fs:report.csv"], sink)

    with pytest.raises(Denied):
        caps.net("hooks.example", "e1")

    assert sink == []
