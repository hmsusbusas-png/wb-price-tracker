"""Клиент публичного API Wildberries: поиск и карточки товаров."""
from __future__ import annotations

import os
from dataclasses import dataclass

import requests

_BASE = os.environ.get("WB_API_BASE", "").rstrip("/")
SEARCH_URL = _BASE + "/exactmatch/ru/common/v5/search" if _BASE else "https://search.wb.ru/exactmatch/ru/common/v5/search"
CARD_URL = _BASE + "/cards/v2/detail" if _BASE else "https://card.wb.ru/cards/v2/detail"

# dest=-1257786 — Москва; без него выдача приходит пустой
COMMON_PARAMS = {"appType": 1, "curr": "rub", "dest": -1257786}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/124.0 Safari/537.36",
    "Accept": "application/json",
}


@dataclass
class Product:
    nm_id: int
    name: str
    brand: str
    price: float        # ₽, со скидкой
    base_price: float   # ₽, до скидки
    rating: float
    feedbacks: int

    @property
    def discount(self) -> int:
        if not self.base_price:
            return 0
        return round((1 - self.price / self.base_price) * 100)

    @property
    def url(self) -> str:
        return f"https://www.wildberries.ru/catalog/{self.nm_id}/detail.aspx"


class WbError(Exception):
    """Проблема при обращении к API: сеть, таймаут, пустой или битый ответ."""


def _rub(kopecks) -> float:
    return round(kopecks / 100, 2)


def _prices(p: dict) -> tuple[float, float]:
    # с 2024 цены переехали внутрь sizes[].price, старые выдачи отдают salePriceU
    for size in p.get("sizes") or []:
        price = size.get("price") or {}
        if price.get("product"):
            return _rub(price["product"]), _rub(price.get("basic") or price["product"])
    if p.get("salePriceU"):
        return _rub(p["salePriceU"]), _rub(p.get("priceU") or p["salePriceU"])
    return 0.0, 0.0


def _parse(p: dict) -> Product:
    price, base = _prices(p)
    return Product(
        nm_id=int(p.get("id") or 0),
        name=p.get("name") or "Без названия",
        brand=(p.get("brand") or "").strip() or "Без бренда",
        price=price,
        base_price=base,
        rating=float(p.get("reviewRating") or p.get("rating") or 0),
        feedbacks=int(p.get("feedbacks") or 0),
    )


def _products_of(data: dict) -> list[dict]:
    """Достаёт список товаров; кривой ответ любого уровня превращается в пустой список."""
    if not isinstance(data, dict):
        return []
    payload = data.get("data") if isinstance(data.get("data"), dict) else data
    products = (payload or {}).get("products") or []
    return [p for p in products if isinstance(p, dict)]


def _get(url: str, params: dict, timeout: float) -> dict:
    try:
        resp = requests.get(url, params=params, headers=HEADERS, timeout=timeout)
    except requests.exceptions.Timeout as e:
        raise WbError(f"WB не ответил за {timeout} с — повторите попытку позже") from e
    except requests.exceptions.RequestException as e:
        raise WbError(f"нет соединения с WB ({e.__class__.__name__}) — проверьте сеть/VPN") from e
    if resp.status_code != 200:
        raise WbError(f"WB вернул HTTP {resp.status_code}")
    try:
        return resp.json()
    except ValueError as e:
        raise WbError("WB отдал ответ не в JSON (возможна блокировка по IP)") from e


def search(query: str, pages: int = 1, timeout: float = 10.0) -> list[Product]:
    found: list[Product] = []
    seen: set[int] = set()
    for page in range(1, pages + 1):
        data = _get(SEARCH_URL, {
            **COMMON_PARAMS,
            "query": query,
            "resultset": "catalog",
            "page": page,
            "sort": "popular",
            "ab_testing": "false",
        }, timeout)
        products = _products_of(data)
        if not products:
            break
        for p in products:
            try:
                pid = int(p.get("id"))
            except (TypeError, ValueError):
                continue  # карточка без валидного id — пропускаем, не роняя выдачу
            if pid not in seen:
                seen.add(pid)
                found.append(_parse(p))
    return found


def get_products(nm_ids: list[int], timeout: float = 10.0) -> list[Product]:
    """Карточки пачкой: card-эндпоинт принимает артикулы через запятую."""
    if not nm_ids:
        return []
    data = _get(CARD_URL, {**COMMON_PARAMS, "spp": 30, "nm": ",".join(map(str, nm_ids))}, timeout)
    parsed: list[Product] = []
    for p in _products_of(data):
        try:
            parsed.append(_parse(p))
        except (KeyError, TypeError, ValueError):
            continue  # кривая карточка не должна ронять весь запрос
    return parsed


def get_product(nm_id: int, timeout: float = 10.0) -> Product:
    found = get_products([nm_id], timeout)
    if not found:
        raise WbError(f"товар {nm_id} не найден — проверьте артикул")
    return found[0]
