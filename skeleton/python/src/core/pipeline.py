from __future__ import annotations

from .contract import Caps, Event, Plugin, PluginPack, Result
from .sandbox import SandboxedCaps


class Sandboxed:
    def __init__(self, inner: Plugin, permissions: list[str],
                 sink: list[tuple[str, str]]) -> None:
        self.id = inner.id
        self._inner = inner
        self._permissions = permissions
        self._sink = sink

    def handle(self, event: Event, caps: Caps) -> Result:
        # Вхідні caps ігноруються навмисно: двері плагіна відчиняє ядро,
        # а не той, хто його викликав.
        return self._inner.handle(event, SandboxedCaps(self._permissions, self._sink))


class Telemetry:
    def __init__(self, inner: Plugin, log: list[str]) -> None:
        self.id = inner.id
        self._inner = inner
        self._log = log

    def handle(self, event: Event, caps: Caps) -> Result:
        self._log.append(f"start {self.id} {event.id}")
        try:
            result = self._inner.handle(event, caps)
        except Exception as error:
            self._log.append(f"fail {self.id} {type(error).__name__}")
            raise
        self._log.append(f"done {self.id} ok={result.ok}")
        return result


def harden(pack: PluginPack, plugin: Plugin, log: list[str],
           sink: list[tuple[str, str]]) -> Plugin:
    # Телеметрія зовні, бо має бачити і відмову пісочниці.
    return Telemetry(Sandboxed(plugin, pack.create_permissions(), sink), log)
