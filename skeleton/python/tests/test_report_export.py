from src.core.contract import Event
from src.core.registry import Runtime


def test_report_export_stores_event_result():
    runtime = Runtime(["report_export"])

    result = runtime.dispatch(
        Event(id="e42", kind="report_export", text="звіт готовий")
    )

    assert result.ok is True
    assert result.ref == "events/e42"