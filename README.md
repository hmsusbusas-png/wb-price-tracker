# wb-price-tracker

Command-line tool for Wildberries: search the catalog for products with prices,
export results to Excel, and track how the price of a specific product changes
over time.

Built on WB's public (unofficial) search and card endpoints — no API key
needed. Useful for sellers watching competitors and for anyone waiting for
a price drop.

## Install

Python 3.10+ (tested on 3.14):

```bash
pip install -r requirements.txt
```

## Usage

Search the catalog:

```console
$ python cli.py search "капучинатор"

  1. Капучинатор ручной для взбивания молока, венчик из н     3 290 ₽  ★4.8 (2431)
  2. Автоматический капучинатор для кофе с подогревом, 4      5 490 ₽  ★4.6 (812)
  3. Венчик для капучинатора, запасной, сталь                   990 ₽  ★4.9 (154)

Всего найдено: 3 товаров
```

Same results as a formatted spreadsheet:

```console
$ python cli.py search "капучинатор" --excel wb_prices.xlsx
Excel сохранён: C:\work\wb-price-tracker\wb_prices.xlsx
```

`--pages N` pulls N pages of results (100 items each).

Start tracking a product (article number from the product URL):

```console
$ python cli.py track 211984736
Отслеживаю: Капучинатор ручной для взбивания молока, венчик из нержавейк — 3 290 ₽
```

Every `check` run polls all tracked products and shows the change since
the previous price:

```console
$ python cli.py check
  Капучинатор ручной для взбивания молока, вен     3 450 ₽  ↑ 160 ₽ (+4.9%)
  Капучинатор ручной для взбивания молока, вен     3 100 ₽  ↓ 350 ₽ (-10.1%)
```

Prices accumulate in `history.json`, so wire `check` into a cron job /
Task Scheduler and you get a price history for free. Plot it:

```console
$ python cli.py chart 211984736
График сохранён: C:\work\wb-price-tracker\price_chart.png
```

Full history in the console:

```console
$ python cli.py history

Капучинатор ручной для взбивания молока, венчик из нержавейк (211984736)
  2026-09-25 18:32       3 290 ₽
  2026-09-25 18:32       3 450 ₽
  2026-09-25 18:32       3 100 ₽
```

## Notes

- WB returns prices in kopecks; the tool converts to rubles. Both the current
  response format (`sizes[].price`) and the legacy one (`salePriceU`) are handled.
- The API is public but unofficial: WB may change the schema or throttle
  aggressive polling. Keep `check` runs reasonable (a few times a day is plenty).
- Errors (timeout, no network, deleted product) print a short message instead
  of a traceback.

## Contact

Telegram: [@lev_backend](https://t.me/lev_backend)

---

## RU

CLI-инструмент для Wildberries: поиск товаров по запросу с ценами, выгрузка
результатов в Excel и отслеживание изменения цены конкретного товара.

Работает через публичные (неофициальные) эндпоинты поиска и карточек — ключ
API не нужен. Полезно продавцам для мониторинга конкурентов и всем, кто ждёт
снижения цены на конкретный товар.

```bash
pip install -r requirements.txt
```

Основные команды:

- `python cli.py search "запрос" --pages 2` — поиск, `--excel file.xlsx` — выгрузка в Excel
- `python cli.py track 211984736` — добавить артикул в отслеживание
- `python cli.py check` — опросить все товары, показать дельту (↑/↓ в рублях и процентах)
- `python cli.py chart 211984736` — график истории цены в PNG
- `python cli.py history` — таблица истории в консоли

Цены копятся в `history.json`: достаточно запускать `check` по расписанию
(планировщик задач / cron), и история цен собирается сама. WB отдаёт цены
в копейках — здесь они переводятся в рубли, поддержаны и новый формат ответа
(`sizes[].price`), и старый (`salePriceU`). Ошибки (таймаут, нет сети, товар
удалён) выводятся коротким сообщением вместо traceback.

Связь: Telegram [@lev_backend](https://t.me/lev_backend)
