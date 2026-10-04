from src.core.contract import Caps, Event, Plugin, Result
from vendor.blobstore import Store


class BlobStoreAdapter:
    def __init__(self, caps: Caps) -> None:
        self._store = Store(
            segments=["reports"],
            wire=caps.net,
        )

    def put_report(self, event_id: str, data: str) -> str:
        handle = self._store.put(
            "reports",
            ["events", event_id],
            data,
        )
        return handle.key


class ReportExportPlugin:
    id = "report_export"

    def handle(self, event: Event, caps: Caps) -> Result:
        adapter = BlobStoreAdapter(caps)
        ref = adapter.put_report(event.id, event.text)
        return Result(ok=True, ref=ref)


class ReportExportPack:
    wraps = None

    def create_plugin(self, inner: Plugin | None) -> Plugin:
        return ReportExportPlugin()

    def create_permissions(self) -> list[str]:
        return ["net:reports.blobs"]


pack = ReportExportPack()