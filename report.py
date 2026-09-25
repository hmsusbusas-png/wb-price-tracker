"""Экспорт результатов: Excel-таблица и PNG-график цены."""
from __future__ import annotations

from pathlib import Path

import pandas as pd
from openpyxl.styles import Alignment, Font, PatternFill

import wb

_PURPLE = "7B2FF7"  # фирменный фиолетовый WB


def to_excel(products: list[wb.Product], path: str) -> Path:
    df = pd.DataFrame([{
        "Артикул": p.nm_id,
        "Название": p.name,
        "Бренд": p.brand,
        "Цена, ₽": p.price,
        "До скидки, ₽": p.base_price,
        "Скидка, %": p.discount,
        "Рейтинг": p.rating,
        "Отзывов": p.feedbacks,
        "Ссылка": p.url,
    } for p in products])

    out = Path(path)
    with pd.ExcelWriter(out, engine="openpyxl") as xl:
        df.to_excel(xl, index=False, sheet_name="Поиск")
        sheet = xl.sheets["Поиск"]
        head_font = Font(bold=True, color="FFFFFF")
        head_fill = PatternFill("solid", fgColor=_PURPLE)
        for cell in sheet[1]:
            cell.font = head_font
            cell.fill = head_fill
            cell.alignment = Alignment(horizontal="center")
        for col, width in {"A": 12, "B": 48, "C": 18, "D": 11, "E": 13,
                           "F": 11, "G": 9, "H": 10, "I": 46}.items():
            sheet.column_dimensions[col].width = width
        sheet.freeze_panes = "A2"
    return out
