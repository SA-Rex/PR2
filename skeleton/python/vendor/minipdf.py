"""Чужий SDK: складач односторінкових документів.

Власна модель: сторінка й блоки, координати задаються від лівого
нижнього кута.
Власні одиниці: усе рахується в пунктах (1/72 дюйма), про міліметри
бібліотека не знає — перерахунок робить той, хто нею користується.
Власні помилки: `OutsidePage`, `EmptyDocument`.

Бібліотека нічого не зберігає — `render()` повертає готовий рядок.
"""

from __future__ import annotations

from dataclasses import dataclass

PT_PER_MM = 72.0 / 25.4
A4_PT = (595.0, 842.0)


class MiniPdfError(Exception):
    """Базова помилка бібліотеки."""


class OutsidePage(MiniPdfError):
    """Блок не вміщається в аркуш."""


class EmptyDocument(MiniPdfError):
    """Документ без жодного блока бібліотека не рендерить."""


@dataclass(frozen=True)
class Block:
    x_pt: float
    y_pt: float
    text: str


class Page:
    def __init__(self, width_pt: float = A4_PT[0],
                 height_pt: float = A4_PT[1]) -> None:
        self.width_pt = width_pt
        self.height_pt = height_pt
        self._blocks: list[Block] = []

    def place(self, block: Block) -> None:
        if not 0.0 <= block.x_pt <= self.width_pt:
            raise OutsidePage(f"x_pt={block.x_pt} поза аркушем")
        if not 0.0 <= block.y_pt <= self.height_pt:
            raise OutsidePage(f"y_pt={block.y_pt} поза аркушем")
        self._blocks.append(block)

    def render(self) -> str:
        if not self._blocks:
            raise EmptyDocument("документ не містить блоків")
        head = f"%MINIPDF-1.0 {self.width_pt:.0f}x{self.height_pt:.0f}pt"
        body = "\n".join(
            f"BT {block.x_pt:.0f} {block.y_pt:.0f} ({block.text}) Tj ET"
            for block in self._blocks
        )
        return f"{head}\n{body}\n%%EOF"
