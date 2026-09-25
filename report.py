"""Экспорт результатов: Excel-таблица и PNG-график цены."""
from __future__ import annotations

from datetime import datetime
from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd
from openpyxl.styles import Alignment, Font, PatternFill

import wb
from storage import get

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


def price_chart(nm_id: int, path: str) -> Path:
    item = get(nm_id)
    if not item:
        raise ValueError(f"товар {nm_id} не отслеживается — сначала `track`")
    points = item["points"]
    if len(points) < 2:
        raise ValueError("нужны минимум 2 замера — запустите `check` ещё раз")

    xs = [datetime.strptime(p["ts"], "%Y-%m-%d %H:%M") for p in points]
    ys = [p["price"] for p in points]

    fig, ax = plt.subplots(figsize=(9, 5), dpi=120)
    fig.patch.set_facecolor("#fafafa")
    ax.set_facecolor("#fafafa")
    ax.plot(xs, ys, color="#7B2FF7", linewidth=2.2, marker="o",
            markersize=5, markerfacecolor="white", markeredgecolor="#7B2FF7")
    ax.fill_between(xs, ys, min(ys) * 0.97, color="#7B2FF7", alpha=0.08)

    for x, y in zip(xs, ys):
        ax.annotate(f"{y:.0f} ₽", (x, y), textcoords="offset points",
                    xytext=(0, 9), ha="center", fontsize=8.5, color="#444")

    ax.set_title(item["name"][:60], fontsize=12, pad=14)
    ax.set_xlabel("Дата замера", fontsize=10)
    ax.set_ylabel("Цена, ₽", fontsize=10)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d.%m %H:%M"))
    ax.grid(True, linestyle="--", alpha=0.35)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()

    out = Path(path)
    fig.savefig(out)
    plt.close(fig)
    return out
