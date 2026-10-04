from pathlib import Path

from src.core.contract import Event
from src.core.registry import Runtime, enabled_plugins

ROOT = Path(__file__).resolve().parents[1]


def test_event_reaches_plugin_of_its_kind():
    runtime = Runtime(["echo"])

    result = runtime.dispatch(Event(id="e1", kind="echo", text="привіт"))

    assert result.ok is True
    assert result.ref == "ПРИВІТ#1"


def test_telemetry_records_start_and_done():
    runtime = Runtime(["echo"])

    runtime.dispatch(Event(id="e1", kind="echo", text="привіт"))

    assert len(runtime.log) == 2
    assert runtime.log[0] == "start echo e1"
    assert runtime.log[1].startswith("done echo ok=")


def test_configuration_lists_enabled_plugins():
    assert "echo" in enabled_plugins(ROOT / "plugins.toml")
