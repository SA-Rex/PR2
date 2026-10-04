"""Чужий SDK: сховище ключ-значення з часом життя.

Власна модель: ключ складений із простору імен і власне ключа,
відсутнє значення — це виняток, а не `None`.
Власні одиниці: час життя задається в годинах, годинник повертає секунди.
Власні помилки: `BadKey`, `NoValue`.

Бібліотека тримає значення в пам'яті й нікуди не ходить.
"""

from __future__ import annotations

from typing import Callable

SECONDS_PER_HOUR = 3600
SEPARATOR = "::"


class KvError(Exception):
    """Базова помилка бібліотеки."""


class BadKey(KvError):
    """Ключ або час життя не відповідають правилам бібліотеки."""


class NoValue(KvError):
    """За ключем нічого немає або значення протермінувалося."""


class KvStore:
    def __init__(self, clock: Callable[[], int], default_ttl_h: int = 1) -> None:
        self._clock = clock
        self._default_ttl_h = default_ttl_h
        self._cells: dict[str, tuple[str, int]] = {}

    @staticmethod
    def compose(namespace: str, key: str) -> str:
        for part in (namespace, key):
            if not part or SEPARATOR in part:
                raise BadKey(f"недопустима частина ключа: {part!r}")
        return f"{namespace}{SEPARATOR}{key}"

    def put(self, namespace: str, key: str, blob: str,
            ttl_h: int | None = None) -> str:
        full = self.compose(namespace, key)
        hours = self._default_ttl_h if ttl_h is None else ttl_h
        if hours <= 0:
            raise BadKey(f"ttl_h має бути додатним: {hours}")
        self._cells[full] = (blob, self._clock() + hours * SECONDS_PER_HOUR)
        return full

    def fetch(self, namespace: str, key: str) -> str:
        full = self.compose(namespace, key)
        cell = self._cells.get(full)
        if cell is None:
            raise NoValue(f"немає значення: {full}")
        blob, dies_at = cell
        if self._clock() >= dies_at:
            del self._cells[full]
            raise NoValue(f"значення протермінувалося: {full}")
        return blob
