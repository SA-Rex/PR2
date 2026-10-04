from __future__ import annotations

import importlib
import tomllib
from pathlib import Path

from .contract import Event, Plugin, Result
from .pipeline import harden
from .sandbox import DENY_ALL


def enabled_plugins(config: Path) -> list[str]:
    return tomllib.loads(config.read_text(encoding="utf-8"))["enabled"]


class Runtime:
    def __init__(self, names: list[str]) -> None:
        self.log: list[str] = []
        self.sink: list[tuple[str, str]] = []
        self._packs = {
            name: importlib.import_module(f"src.plugins.{name}.plugin").pack
            for name in names
        }
        self._plugins: dict[str, Plugin] = {}
        self._build()

    def _build(self) -> None:
        for pack in self._packs.values():          # спершу самостійні плагіни
            if pack.wraps is None:
                plugin = pack.create_plugin(None)
                self._plugins[plugin.id] = harden(pack, plugin, self.log, self.sink)
        for pack in self._packs.values():          # потім обгортки над ними
            if pack.wraps is not None:
                inner = self._plugins[pack.wraps]
                plugin = pack.create_plugin(inner)  # id лишається тим самим
                self._plugins[plugin.id] = harden(pack, plugin, self.log, self.sink)

    def dispatch(self, event: Event) -> Result:
        return self._plugins[event.kind].handle(event, DENY_ALL)
