"""Menyu va do'kon sozlamalari: yuklash, narxni hisoblash, ish vaqti."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, time, timedelta, timezone
from pathlib import Path
from typing import Any

# O'zbekistonda yozgi vaqt yo'q — doim UTC+5.
TASHKENT_TZ = timezone(timedelta(hours=5), name="Asia/Tashkent")

MAX_QTY_PER_ITEM = 50
MAX_LINES = 40
ORDER_TYPES = ("delivery", "pickup")
PAYMENT_METHODS = ("cash", "click", "payme")


class OrderError(Exception):
    """Buyurtmani qabul qilib bo'lmaydi. `code` — mijozga ko'rsatiladigan xato kaliti."""

    def __init__(self, code: str, **details: Any) -> None:
        super().__init__(code)
        self.code = code
        self.details = details


@dataclass
class Line:
    product_id: str
    name: dict[str, str]
    price: int
    qty: int

    @property
    def total(self) -> int:
        return self.price * self.qty

    def as_dict(self) -> dict[str, Any]:
        return {"id": self.product_id, "name": self.name, "price": self.price, "qty": self.qty}


@dataclass
class Quote:
    lines: list[Line]
    subtotal: int
    delivery_fee: int
    total: int


def fmt_money(amount: int, lang: str = "uz") -> str:
    cur = "сум" if lang == "ru" else "so'm"
    return f"{amount:,}".replace(",", " ") + f" {cur}"


def _parse_hhmm(value: str) -> time:
    h, m = value.split(":")
    return time(int(h), int(m))


@dataclass
class Catalog:
    store: dict[str, Any]
    categories: list[dict[str, Any]]
    products: dict[str, dict[str, Any]]
    stoplist: set[str] = field(default_factory=set)

    # ---------- yuklash ----------
    @classmethod
    def load(cls, data_dir: Path) -> "Catalog":
        store = json.loads((data_dir / "store.json").read_text(encoding="utf-8"))
        menu = json.loads((data_dir / "menu.json").read_text(encoding="utf-8"))
        categories = menu["categories"]
        cat_ids = {c["id"] for c in categories}
        products: dict[str, dict[str, Any]] = {}
        for p in menu["products"]:
            if p["id"] in products:
                raise ValueError(f"menu.json: takrorlangan mahsulot id: {p['id']}")
            if p["category"] not in cat_ids:
                raise ValueError(f"menu.json: {p['id']} uchun noma'lum kategoriya {p['category']}")
            if not isinstance(p["price"], int) or p["price"] <= 0:
                raise ValueError(f"menu.json: {p['id']} narxi musbat butun son bo'lishi kerak")
            products[p["id"]] = p
        return cls(store=store, categories=categories, products=products)

    # ---------- ish vaqti ----------
    def is_open(self, now: datetime | None = None) -> bool:
        hours = self.store.get("hours") or {}
        if not hours.get("open") or not hours.get("close"):
            return True
        now = (now or datetime.now(TASHKENT_TZ)).astimezone(TASHKENT_TZ)
        start, end, cur = _parse_hhmm(hours["open"]), _parse_hhmm(hours["close"]), now.time()
        if start == end:
            return True  # 24/7
        if start < end:
            return start <= cur < end
        # Yarim tundan o'tib ishlaydi (masalan 10:00–02:00)
        return cur >= start or cur < end

    # ---------- menyu ----------
    def is_available(self, product_id: str) -> bool:
        p = self.products.get(product_id)
        return bool(p) and product_id not in self.stoplist and p.get("available", True)

    def public_menu(self) -> dict[str, Any]:
        items = []
        for p in self.products.values():
            items.append({
                "id": p["id"],
                "category": p["category"],
                "name": p["name"],
                "description": p.get("description") or {},
                "price": p["price"],
                "image": p.get("image") or "",
                "badge": p.get("badge") or "",
                "available": self.is_available(p["id"]),
            })
        return {"categories": self.categories, "products": items}

    def public_store(self) -> dict[str, Any]:
        s = self.store
        return {
            "name": s.get("name", "Ayva Burgers"),
            "tagline": s.get("tagline", {}),
            "phone": s.get("phone", ""),
            "address": s.get("address", {}),
            "location": s.get("location"),
            "hours": s.get("hours", {}),
            "is_open": self.is_open(),
            "delivery": s.get("delivery", {}),
            "pickup": s.get("pickup", {}),
            "payments": s.get("payments", {"cash": True}),
        }

    # ---------- hisob-kitob ----------
    def delivery_fee(self, subtotal: int, order_type: str) -> int:
        if order_type != "delivery":
            return 0
        d = self.store.get("delivery", {})
        free_from = int(d.get("free_from") or 0)
        if free_from and subtotal >= free_from:
            return 0
        return int(d.get("fee") or 0)

    def quote(self, raw_items: Any, order_type: str) -> Quote:
        """Narxlar faqat serverda hisoblanadi — mijoz yuborgan narxga ishonilmaydi."""
        if order_type not in ORDER_TYPES:
            raise OrderError("bad_type")
        type_cfg = self.store.get(order_type, {})
        if not type_cfg.get("enabled", True):
            raise OrderError("type_disabled")
        if not isinstance(raw_items, list) or not raw_items:
            raise OrderError("empty_cart")
        if len(raw_items) > MAX_LINES:
            raise OrderError("too_many_items")

        merged: dict[str, int] = {}
        for item in raw_items:
            if not isinstance(item, dict):
                raise OrderError("bad_item")
            pid, qty = item.get("id"), item.get("qty")
            if not isinstance(pid, str) or pid not in self.products:
                raise OrderError("unknown_product", product_id=str(pid))
            if not isinstance(qty, int) or isinstance(qty, bool) or qty < 1:
                raise OrderError("bad_qty")
            merged[pid] = merged.get(pid, 0) + qty

        lines: list[Line] = []
        for pid, qty in merged.items():
            if qty > MAX_QTY_PER_ITEM:
                raise OrderError("bad_qty")
            if not self.is_available(pid):
                raise OrderError("unavailable", product_id=pid, name=self.products[pid]["name"])
            p = self.products[pid]
            lines.append(Line(product_id=pid, name=p["name"], price=p["price"], qty=qty))

        subtotal = sum(line.total for line in lines)
        min_order = int(type_cfg.get("min_order") or 0)
        if subtotal < min_order:
            raise OrderError("min_order", min_order=min_order)
        fee = self.delivery_fee(subtotal, order_type)
        return Quote(lines=lines, subtotal=subtotal, delivery_fee=fee, total=subtotal + fee)
