"""wb-price-tracker — поиск товаров и отслеживание цен на Wildberries."""
from __future__ import annotations

import argparse
import sys

import wb


def _fmt(price: float) -> str:
    return f"{price:,.0f}".replace(",", " ")


def cmd_search(args) -> None:
    try:
        products = wb.search(args.query, pages=args.pages)
    except wb.WbError as e:
        sys.exit(f"Ошибка: {e}")
    if not products:
        sys.exit(f"По запросу «{args.query}» ничего не найдено")

    for i, p in enumerate(products[:30], 1):
        print(f"{i:>3}. {p.name[:52]:<52} {_fmt(p.price):>9} ₽  ★{p.rating:.1f} ({p.feedbacks})")
    print(f"\nВсего найдено: {len(products)} товаров")


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="wb-price-tracker",
        description="Поиск товаров и отслеживание цен на Wildberries")
    sub = parser.add_subparsers(dest="command", required=True)

    p_search = sub.add_parser("search", help="поиск товаров по запросу")
    p_search.add_argument("query", help="поисковый запрос")
    p_search.add_argument("--pages", type=int, default=1,
                          help="сколько страниц выдачи (по 100 товаров)")
    p_search.set_defaults(func=cmd_search)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
