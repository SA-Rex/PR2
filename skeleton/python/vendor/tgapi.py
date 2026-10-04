"""Чужий SDK: клієнт месенджера.

Власна модель: відповідь — вкладений словник `{"ok": ..., "result": {...}}`.
Власні одиниці: вікно обмеження швидкості задається у хвилинах,
додатний `chat_id` — приватний чат, від'ємний — група.
Власні помилки: єдиний тип `TgError` із числовим кодом усередині.

Назовні бібліотека сама не ходить: транспорт передається в конструктор.
"""

from __future__ import annotations

from typing import Callable

ERR_CHAT_UNKNOWN = 400
ERR_TEXT_EMPTY = 402
ERR_FLOOD = 429


class TgError(Exception):
    def __init__(self, code: int, description: str) -> None:
        super().__init__(f"{code}: {description}")
        self.code = code
        self.description = description


class Bot:
    def __init__(self, token: str, wire: Callable[[str, str], str],
                 window_min: int = 1, max_per_window: int = 3) -> None:
        self._token = token
        self._wire = wire
        self._window_min = window_min
        self._max_per_window = max_per_window
        self._sent = 0

    @property
    def endpoint(self) -> str:
        return f"api.tg/{self._token}"

    def send_message(self, chat_id: int, msg: str,
                     silent: bool = False) -> dict[str, object]:
        if chat_id == 0:
            raise TgError(ERR_CHAT_UNKNOWN, "chat not found")
        if not msg.strip():
            raise TgError(ERR_TEXT_EMPTY, "message text is empty")
        if self._sent >= self._max_per_window:
            raise TgError(ERR_FLOOD, f"retry after {self._window_min} min")
        self._sent += 1
        handle = self._wire(self.endpoint, f"{chat_id}:{msg}")
        return {
            "ok": True,
            "result": {
                "message_id": self._sent,
                "chat": {"id": chat_id, "group": chat_id < 0},
                "silent": silent,
                "handle": handle,
            },
        }
