"""Чужий SDK: поштовий шлюз.

Власна модель: лист — це `Letter` з полями `to_box`, `head`, `lines`.
Власні одиниці: адреса записується як `user%domain`, розмір листа
рахується в блоках по 64 символи.
Власні помилки: `MailerRejected`, `MailerTooBig`.

Назовні бібліотека сама не ходить: транспорт передається в конструктор.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

BLOCK_CHARS = 64


class MailerError(Exception):
    """Базова помилка бібліотеки."""


class MailerRejected(MailerError):
    """Адреса не у форматі `user%domain`."""


class MailerTooBig(MailerError):
    """Лист довший за дозволену кількість блоків."""


@dataclass(frozen=True)
class Letter:
    to_box: str
    head: str
    lines: tuple[str, ...] = field(default=())


class Gateway:
    def __init__(self, wire: Callable[[str, str], str],
                 host: str = "mail.gateway", max_blocks: int = 4) -> None:
        self._wire = wire
        self._host = host
        self._max_blocks = max_blocks

    @property
    def host(self) -> str:
        return self._host

    @staticmethod
    def box(local: str, domain: str) -> str:
        if not local or not domain:
            raise MailerRejected(f"порожня частина адреси: {local!r}%{domain!r}")
        return f"{local}%{domain}"

    def post(self, letter: Letter) -> str:
        parts = letter.to_box.split("%")
        if len(parts) != 2 or not all(parts):
            raise MailerRejected(f"адреса не у форматі user%domain: {letter.to_box!r}")
        if not letter.head:
            raise MailerRejected("лист без теми шлюз не приймає")
        text = "\n".join(letter.lines)
        blocks = -(-len(text) // BLOCK_CHARS)
        if blocks > self._max_blocks:
            raise MailerTooBig(f"{blocks} блоків при межі {self._max_blocks}")
        handle = self._wire(self._host, f"{letter.to_box}|{letter.head}|{text}")
        return f"queued:{handle}"
