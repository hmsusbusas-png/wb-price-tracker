"""wb-price-tracker — поиск товаров и отслеживание цен на Wildberries."""
from __future__ import annotations

import argparse
import sys

import wb
import report
from storage import add, append_price, get, last_price, tracked_ids


def _fmt(price: float) -> str:
    return f"{price:,.0f}".replace(",", " ")


def _arrow(prev: float, current: float) -> str:
    diff = current - prev
    mark = "↑" if diff > 0 else "↓"
    if prev == 0:  # процент от нуля не считается — показываем только рубли
        return f"{mark} {_fmt(abs(diff))} ₽"
    return f"{mark} {_fmt(abs(diff))} ₽ ({diff / prev * 100:+.1f}%)"


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

    if args.excel:
        path = report.to_excel(products, args.excel)
        print(f"Excel сохранён: {path.resolve()}")


def cmd_track(args) -> None:
    try:
        product = wb.get_product(args.nm_id)
    except wb.WbError as e:
        sys.exit(f"Ошибка: {e}")
    if product.price <= 0:
        sys.exit("Ошибка: WB не вернул цену для этого товара, отслеживание не добавлено")
    if add(product.nm_id, product.name, product.price):
        print(f"Отслеживаю: {product.name[:60]} — {_fmt(product.price)} ₽")
    else:
        print(f"Товар {args.nm_id} уже отслеживается — используйте `check`")


def cmd_check(args) -> None:
    ids = tracked_ids()
    if not ids:
        sys.exit("Список пуст — добавьте товары через `track <артикул>`")
    try:
        products = wb.get_products(ids)
    except wb.WbError as e:
        sys.exit(f"Ошибка: {e}")
    by_id = {p.nm_id: p for p in products}
    for nm_id in ids:
        product = by_id.get(nm_id)
        if not product:
            print(f"  {nm_id}: не найден на WB (товар удалён?)")
            continue
        prev = last_price(nm_id)
        if product.price <= 0:
            # цена не распарсилась (0 ₽) — не пишем мусор в историю
            print(f"  {product.name[:44]:<44}      —  цена не получена, замер пропущен")
            continue
        if prev is None or prev != product.price:
            append_price(nm_id, product.price, product.name)
        delta = "" if prev is None or prev == product.price else _arrow(prev, product.price)
        print(f"  {product.name[:44]:<44} {_fmt(product.price):>9} ₽  {delta}")


def cmd_history(args) -> None:
    ids = tracked_ids()
    if not ids:
        sys.exit("Список пуст — добавьте товары через `track <артикул>`")
    for nm_id in ids:
        item = get(nm_id)
        print(f"\n{item['name'][:60]} ({nm_id})")
        for point in item["points"][-10:]:
            print(f"  {point['ts']}   {_fmt(point['price']):>9} ₽")


def cmd_chart(args) -> None:
    try:
        path = report.price_chart(args.nm_id, args.out)
    except ValueError as e:
        sys.exit(f"Ошибка: {e}")
    print(f"График сохранён: {path.resolve()}")


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="wb-price-tracker",
        description="Поиск товаров и отслеживание цен на Wildberries")
    sub = parser.add_subparsers(dest="command", required=True)

    p_search = sub.add_parser("search", help="поиск товаров по запросу")
    p_search.add_argument("query", help="поисковый запрос")
    p_search.add_argument("--pages", type=int, default=1,
                          help="сколько страниц выдачи (по 100 товаров)")
    p_search.add_argument("--excel", metavar="FILE.xlsx",
                          help="сохранить результаты в Excel")
    p_search.set_defaults(func=cmd_search)

    p_track = sub.add_parser("track", help="добавить товар в отслеживание")
    p_track.add_argument("nm_id", type=int, help="артикул товара")
    p_track.set_defaults(func=cmd_track)

    sub.add_parser("check", help="опросить отслеживаемые товары, показать дельту"
                   ).set_defaults(func=cmd_check)

    sub.add_parser("history", help="история цен из history.json"
                   ).set_defaults(func=cmd_history)

    p_chart = sub.add_parser("chart", help="график истории цены в PNG")
    p_chart.add_argument("nm_id", type=int, help="артикул товара")
    p_chart.add_argument("--out", default="price_chart.png", help="имя файла PNG")
    p_chart.set_defaults(func=cmd_chart)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
