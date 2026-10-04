"""Чужий SDK: об'єктне сховище звітів.

Власна модель: сегменти оголошуються наперед, ключ збирається з частин,
відповідь на запис — `Handle`, а не рядок.
Власні одиниці: розмір об'єкта рахується в кібібайтах, округлених угору.
Власні помилки: `NoSuchSegment`, `NoSuchObject`, `BlobTooLarge`.

Транспорт обов'язковий: кожен запис — ключ і вміст — бібліотека віддає
йому ще до того, як покласти об'єкт; сама вона назовні не ходить.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

KIB = 1024


class BlobError(Exception):
    """Базова помилка бібліотеки."""


class NoSuchSegment(BlobError):
    """Сегмент не оголошено при створенні сховища."""


class NoSuchObject(BlobError):
    """За зібраним ключем у сегменті нічого немає."""


class BlobTooLarge(BlobError):
    """Об'єкт більший за дозволений розмір у кібібайтах."""


@dataclass(frozen=True)
class Handle:
    etag: str
    key: str
    size_kib: int


class Store:
    def __init__(self, segments: list[str], wire: Callable[[str, str], str],
                 limit_kib: int = 8) -> None:
        self._segments = set(segments)
        self._limit_kib = limit_kib
        self._wire = wire
        self._objects: dict[tuple[str, str], str] = {}

    @staticmethod
    def join(parts: list[str]) -> str:
        return "/".join(part.strip("/") for part in parts if part.strip("/"))

    @staticmethod
    def etag(data: str) -> str:
        checksum = 0
        for char in data:
            checksum = (checksum * 131 + ord(char)) % 0xFFFF
        return f"{len(data):04x}{checksum:04x}"

    def _segment(self, segment: str) -> str:
        if segment not in self._segments:
            raise NoSuchSegment(f"сегмент не оголошено: {segment!r}")
        return segment

    def put(self, segment: str, key_parts: list[str], data: str) -> Handle:
        self._segment(segment)
        size_kib = -(-len(data.encode("utf-8")) // KIB)
        if size_kib > self._limit_kib:
            raise BlobTooLarge(f"{size_kib} KiB при межі {self._limit_kib} KiB")
        key = self.join(key_parts)
        if not key:
            raise NoSuchObject("ключ не зібрався з переданих частин")
        self._wire(f"{segment}.blobs", f"{key}\n{data}")
        self._objects[(segment, key)] = data
        return Handle(etag=self.etag(data), key=key, size_kib=size_kib)

    def get(self, segment: str, key_parts: list[str]) -> str:
        self._segment(segment)
        key = self.join(key_parts)
        if (segment, key) not in self._objects:
            raise NoSuchObject(f"немає об'єкта: {segment}/{key}")
        return self._objects[(segment, key)]
