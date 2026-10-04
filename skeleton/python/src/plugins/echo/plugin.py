from src.core.contract import Caps, Event, Plugin, Result


class EchoPlugin:
    id = "echo"

    def __init__(self) -> None:
        self._seen = 0

    def handle(self, event: Event, caps: Caps) -> Result:
        self._seen += 1
        return Result(ok=True, ref=f"{event.text.upper()}#{self._seen}")


class EchoPack:
    wraps = None

    def create_plugin(self, inner: Plugin | None) -> Plugin:
        return EchoPlugin()

    def create_permissions(self) -> list[str]:
        return []


pack = EchoPack()
