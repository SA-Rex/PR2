"""Чужий SDK: HTTP-подібний клієнт.

Власна модель: відповідь — це `Reply`, а не рядок.
Власні одиниці: код відповіді записаний десятками (20, 40, 50),
час очікування — у децисекундах.
Власні помилки: `HttpishRefused`, `HttpishTimeout`.

Назовні бібліотека сама не ходить: транспорт передається в конструктор.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

ACCEPTED = 20
CLIENT_FAULT = 40
SERVER_FAULT = 50


class HttpishError(Exception):
    """Базова помилка бібліотеки."""


class HttpishRefused(HttpishError):
    """Запит не відповідає правилам бібліотеки і не пішов у транспорт."""


class HttpishTimeout(HttpishError):
    """Вичерпано час очікування, заданий у децисекундах."""


@dataclass(frozen=True)
class Reply:
    code: int
    payload: str

    def accepted(self) -> bool:
        return self.code == ACCEPTED


class Client:
    def __init__(self, host: str, wire: Callable[[str, str], str],
                 timeout_ds: int = 30) -> None:
        self._host = host
        self._wire = wire
        self._timeout_ds = timeout_ds

    @property
    def host(self) -> str:
        return self._host

    def send(self, route: str, fields: dict[str, str]) -> Reply:
        if self._timeout_ds <= 0:
            raise HttpishTimeout(f"timeout_ds={self._timeout_ds}")
        if not route.startswith("/"):
            raise HttpishRefused(f"маршрут має починатися з '/': {route!r}")
        if not fields:
            raise HttpishRefused("запит без полів бібліотека не приймає")
        body = "&".join(f"{name}={fields[name]}" for name in sorted(fields))
        handle = self._wire(self._host, f"{route}?{body}")
        if not handle:
            return Reply(code=SERVER_FAULT, payload="")
        return Reply(code=ACCEPTED, payload=handle)
