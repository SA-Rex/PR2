from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class Event:
    id: str
    kind: str
    text: str


@dataclass(frozen=True)
class Result:
    ok: bool
    ref: str


class Caps(Protocol):
    """Єдині двері плагіна назовні. Відчиняє їх ядро, а не плагін."""

    def net(self, host: str, body: str) -> str: ...
    def fs_write(self, name: str, data: str) -> str: ...


class Plugin(Protocol):
    id: str

    def handle(self, event: Event, caps: Caps) -> Result: ...


class PluginPack(Protocol):
    """Abstract Factory: сімейство артефактів одного плагіна."""

    wraps: str | None

    def create_plugin(self, inner: Plugin | None) -> Plugin: ...
    def create_permissions(self) -> list[str]: ...
