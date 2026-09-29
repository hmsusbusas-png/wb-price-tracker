"""История цен: хранится в history.json рядом с местом запуска."""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

HISTORY_FILE = Path("history.json")


def _load() -> dict:
    if not HISTORY_FILE.exists():
        return {}
    try:
        return json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        backup = HISTORY_FILE.with_name(f"{HISTORY_FILE.stem}.broken-{stamp}{HISTORY_FILE.suffix}")
        try:
            HISTORY_FILE.replace(backup)
            print(f"ВНИМАНИЕ: {HISTORY_FILE} повреждён ({e}).\n"
                  f"  Копия сохранена как {backup.name}; история начинается заново.")
        except OSError:
            print(f"ВНИМАНИЕ: {HISTORY_FILE} повреждён ({e}), сохранить копию не удалось — "
                  f"почините или удалите файл вручную.")
        return {}
    except OSError as e:
        print(f"ВНИМАНИЕ: не удалось прочитать {HISTORY_FILE} ({e}) — "
              f"работаем с пустой историей, файл не тронут.")
        return {}


def _save(data: dict) -> None:
    HISTORY_FILE.write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def _now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M")


def tracked_ids() -> list[int]:
    return sorted(int(k) for k in _load())


def get(nm_id: int) -> dict | None:
    return _load().get(str(nm_id))


def last_price(nm_id: int) -> float | None:
    item = get(nm_id)
    if item and item["points"]:
        return item["points"][-1]["price"]
    return None


def add(nm_id: int, name: str, price: float) -> bool:
    """Добавляет товар. False — если уже отслеживается."""
    if price <= 0:
        return False
    data = _load()
    if str(nm_id) in data:
        return False
    data[str(nm_id)] = {
        "name": name,
        "points": [{"ts": _now(), "price": price}],
    }
    _save(data)
    return True


def append_price(nm_id: int, price: float, name: str | None = None) -> None:
    if price <= 0:
        return
    data = _load()
    item = data.setdefault(str(nm_id), {"name": name or f"Товар {nm_id}", "points": []})
    if name:
        item["name"] = name
    item["points"].append({"ts": _now(), "price": price})
    _save(data)
