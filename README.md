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

Search the catalog (output format shown schematically):

```console
$ python cli.py search "капучинатор" --pages 1

  1. <название товара>                3 290 ₽  ★4.8 (2431)
  2. <название товара>                1 190 ₽  ★4.6 (812)

Всего найдено: 47 товаров
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
Отслеживаю: <название товара> — 3 290 ₽
```

Every `check` run polls all tracked products and shows the change since
the previous recorded price (no line for a product means no change since
the last run):

```console
$ python cli.py check
  <название товара>     3 450 ₽  ↑ 160 ₽ (+4.9%)
```

A measurement is recorded in `history.json` only when the price actually
changed (or on the very first check), so the history stays clean. Wire
`check` into a cron job / Task Scheduler and you get a price history for
free. Plot it:

```console
$ python cli.py chart 211984736
График сохранён: C:\work\wb-price-tracker\price_chart.png
```

Full history in the console (one line per recorded measurement):

```console
$ python cli.py history
<название товара> (211984736)
  <дата время>       3 290 ₽
  <дата время>       3 100 ₽
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

Цены копятся в `history.json`: замер записывается только когда цена
реально изменилась (или при первом `check`), поэтому история остаётся
чистой. Достаточно запускать `check` по расписанию (планировщик задач /
cron), и история цен собирается сама. WB отдаёт цены в копейках — здесь
они переводятся в рубли, поддержаны и новый формат ответа
(`sizes[].price`), и старый (`salePriceU`). Ошибки (таймаут, нет сети,
товар удалён) выводятся коротким сообщением вместо traceback; если
`history.json` повреждён, перед началом новой истории сохраняется копия
`history.broken-<дата>.json`.

Связь: Telegram [@lev_backend](https://t.me/lev_backend)
