"""Menyu va do'kon sozlamalari (bazadan xotiraga yuklanadi): narx, aksiya, ish vaqti."""
from __future__ import annotations

import copy
import json
import math
from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta, timezone
from typing import Any

# O'zbekistonda yozgi vaqt yo'q — doim UTC+5.
TASHKENT_TZ = timezone(timedelta(hours=5), name="Asia/Tashkent")

MAX_QTY_PER_ITEM = 50
MAX_LINES = 40
ORDER_TYPES = ("delivery", "pickup")
# To'lov — faqat naqd pul (kuryerga yoki kassada).
PAYMENT_METHODS = ("cash",)
BADGES = ("", "hit", "new", "spicy")
ICONS = ("burger", "pizza", "combo", "hotdog", "fries", "sauce", "drink", "wrap", "chicken", "dessert")
MAX_VARIANTS = 12

DEFAULT_STORE: dict[str, Any] = {
    "name": "Ayva Burgers",
    "tagline": {"uz": "", "ru": ""},
    "about": {"uz": "", "ru": ""},
    "phone": "",
    "support_username": "",
    "instagram": "",
    "address": {"uz": "", "ru": ""},
    "location": None,
    "hours": {"open": "10:00", "close": "02:00"},
    "accepting": True,
    "delivery": {"enabled": True, "fee": 0, "free_from": 0, "min_order": 0, "eta": ""},
    "pickup": {"enabled": True, "min_order": 0, "eta": ""},
    "payments": {"cash": True},
}


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
    variant: int | None = None

    @property
    def total(self) -> int:
        return self.price * self.qty

    def as_dict(self) -> dict[str, Any]:
        d = {"id": self.product_id, "name": self.name, "price": self.price, "qty": self.qty}
        if self.variant is not None:
            d["v"] = self.variant
        return d


@dataclass
class Quote:
    lines: list[Line]
    subtotal: int
    delivery_fee: int
    total: int


def fmt_money(amount: int, lang: str = "uz") -> str:
    cur = "сум" if lang == "ru" else "so'm"
    return f"{amount:,}".replace(",", " ") + f" {cur}"


def today_local() -> date:
    return datetime.now(TASHKENT_TZ).date()


def _parse_hhmm(value: str) -> time:
    h, m = value.split(":")
    return time(int(h), int(m))


def hours_open(open_s: str | None, close_s: str | None, now: datetime | None = None) -> bool:
    """Ish vaqti ichidami. open == close — 24/7; close < open — yarim tundan o'tib ishlaydi."""
    if not open_s or not close_s:
        return True
    now = (now or datetime.now(TASHKENT_TZ)).astimezone(TASHKENT_TZ)
    start, end, cur = _parse_hhmm(open_s), _parse_hhmm(close_s), now.time()
    if start == end:
        return True
    if start < end:
        return start <= cur < end
    return cur >= start or cur < end


def distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = math.radians(lat2 - lat1), math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def branch_from_row(r: dict[str, Any]) -> dict[str, Any]:
    has_loc = r.get("lat") is not None and r.get("lon") is not None
    return {
        "id": r["id"], "name": _i18n(r["name_uz"], r["name_ru"]), "address": _i18n(r["address_uz"], r["address_ru"]),
        "phone": r.get("phone") or "", "hours": {"open": r["open"], "close": r["close"]},
        "location": {"lat": r["lat"], "lon": r["lon"]} if has_loc else None,
        "chat_id": r.get("chat_id"), "active": bool(r.get("active", 1)),
    }


def _merge(base: dict[str, Any], extra: dict[str, Any]) -> dict[str, Any]:
    out = copy.deepcopy(base)
    for k, v in (extra or {}).items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _merge(out[k], v)
        else:
            out[k] = v
    return out


def normalize_store(raw: dict[str, Any] | None) -> dict[str, Any]:
    store = _merge(DEFAULT_STORE, raw or {})
    store["payments"] = {"cash": True}
    store.pop("branches", None)
    return store


def _i18n(uz: str, ru: str) -> dict[str, str]:
    return {"uz": uz or "", "ru": ru or uz or ""}


def category_from_row(r: dict[str, Any]) -> dict[str, Any]:
    return {"id": r["id"], "name": _i18n(r["name_uz"], r["name_ru"]), "icon": r["icon"] or "burger",
            "visible": bool(r["visible"]), "sort": r["sort"]}


def parse_variants(raw: Any) -> list[dict[str, Any]]:
    """Bazadagi JSON ([{uz, ru, price}]) -> [{name: {uz, ru}, price}]."""
    if not raw:
        return []
    items = json.loads(raw) if isinstance(raw, str) else raw
    return [{"name": _i18n(v.get("uz", ""), v.get("ru", "")), "price": int(v["price"])} for v in items]


def variant_label(name: dict[str, str], variant: dict[str, Any]) -> dict[str, str]:
    return {lang: f"{name[lang]} ({variant['name'][lang]})" for lang in ("uz", "ru")}


def product_from_row(r: dict[str, Any]) -> dict[str, Any]:
    return {
        "variants": parse_variants(r.get("variants")),
        "id": r["id"], "category": r["category_id"],
        "name": _i18n(r["name_uz"], r["name_ru"]),
        "description": _i18n(r["desc_uz"], r["desc_ru"]),
        "price": int(r["price"]), "promo_price": r["promo_price"],
        "promo_from": r["promo_from"], "promo_to": r["promo_to"],
        "image": r["image"] or "", "badge": r["badge"] or "",
        "available": bool(r["available"]), "visible": bool(r["visible"]), "sort": r["sort"],
    }


def promo_active(p: dict[str, Any], today: date | None = None) -> bool:
    pp = p.get("promo_price")
    if not pp or pp >= p["price"]:
        return False
    today = today or today_local()
    if p.get("promo_from") and today < date.fromisoformat(p["promo_from"]):
        return False
    if p.get("promo_to") and today > date.fromisoformat(p["promo_to"]):
        return False
    return True


def banner_active(b: dict[str, Any], today: date | None = None) -> bool:
    if not b.get("active"):
        return False
    today = today or today_local()
    if b.get("date_from") and today < date.fromisoformat(b["date_from"]):
        return False
    if b.get("date_to") and today > date.fromisoformat(b["date_to"]):
        return False
    return True


@dataclass
class Catalog:
    store: dict[str, Any]
    categories: list[dict[str, Any]]
    products: dict[str, dict[str, Any]]
    banners: list[dict[str, Any]] = field(default_factory=list)
    branches: list[dict[str, Any]] = field(default_factory=list)

    # ---------- yuklash ----------
    @classmethod
    async def from_db(cls, db: Any) -> "Catalog":
        store = await db.get_setting("store")
        cats = [category_from_row(r) for r in await db.list_categories()]
        prods = {r["id"]: product_from_row(r) for r in await db.list_products()}
        return cls(store=normalize_store(store), categories=cats, products=prods,
                   banners=await db.list_banners(),
                   branches=[branch_from_row(r) for r in await db.list_branches()])

    def category(self, cat_id: str) -> dict[str, Any] | None:
        return next((c for c in self.categories if c["id"] == cat_id), None)

    # ---------- ish vaqti ----------
    # ---------- filiallar ----------
    def active_branches(self) -> list[dict[str, Any]]:
        return [b for b in self.branches if b["active"]]

    def branch(self, branch_id: str | None) -> dict[str, Any] | None:
        return next((b for b in self.branches if b["id"] == branch_id), None)

    @staticmethod
    def branch_open(b: dict[str, Any], now: datetime | None = None) -> bool:
        return hours_open(b["hours"]["open"], b["hours"]["close"], now)

    def nearest_branch(self, lat: float | None, lon: float | None, now: datetime | None = None,
                       only_open: bool = True) -> dict[str, Any] | None:
        pool = [b for b in self.active_branches() if not only_open or self.branch_open(b, now)]
        if not pool:
            return None
        if lat is not None and lon is not None:
            located = [b for b in pool if b["location"]]
            if located:
                return min(located, key=lambda b: distance_km(lat, lon, b["location"]["lat"], b["location"]["lon"]))
        return pool[0]

    def pick_branch(self, order_type: str, branch_id: str | None = None, lat: float | None = None,
                    lon: float | None = None, now: datetime | None = None) -> dict[str, Any] | None:
        """Buyurtmani tayyorlaydigan filial. Filiallar bo'lmasa — None (bitta do'kon rejimi)."""
        if not self.active_branches():
            return None
        if branch_id:
            b = self.branch(branch_id)
            if not b or not b["active"]:
                raise OrderError("bad_branch")
            if not self.branch_open(b, now):
                raise OrderError("branch_closed", branch=b["name"])
            return b
        b = self.nearest_branch(lat if order_type == "delivery" else None,
                                lon if order_type == "delivery" else None, now)
        if b is None:
            raise OrderError("closed")
        return b

    def within_hours(self, now: datetime | None = None) -> bool:
        branches = self.active_branches()
        if branches:
            return any(self.branch_open(b, now) for b in branches)
        hours = self.store.get("hours") or {}
        return hours_open(hours.get("open"), hours.get("close"), now)

    def is_open(self, now: datetime | None = None) -> bool:
        """Hozir buyurtma qabul qilinadimi: admin to'xtatmagan va ish vaqti."""
        return bool(self.store.get("accepting", True)) and self.within_hours(now)

    # ---------- menyu ----------
    def is_shown(self, product_id: str) -> bool:
        p = self.products.get(product_id)
        if not p or not p["visible"]:
            return False
        cat = self.category(p["category"])
        return bool(cat and cat["visible"])

    def is_available(self, product_id: str) -> bool:
        return self.is_shown(product_id) and self.products[product_id]["available"]

    def price_of(self, product_id: str, today: date | None = None, variant: int | None = None) -> tuple[int, int | None]:
        """(amaldagi narx, eski narx yoki None). Variantli mahsulotda aksiya foizi har bir variantga qo'llanadi."""
        p = self.products[product_id]
        base = p["variants"][variant]["price"] if variant is not None and p["variants"] else p["price"]
        if not promo_active(p, today):
            return base, None
        if base == p["price"]:
            return int(p["promo_price"]), base
        ratio = int(p["promo_price"]) / p["price"]
        return max(100, round(base * ratio / 100) * 100), base

    def public_menu(self) -> dict[str, Any]:
        today = today_local()
        cats = [{"id": c["id"], "name": c["name"], "icon": c["icon"]} for c in self.categories if c["visible"]]
        items = []
        for p in self.products.values():
            if not self.is_shown(p["id"]):
                continue
            price, old = self.price_of(p["id"], today)
            variants = []
            for i, v in enumerate(p["variants"]):
                vp, vo = self.price_of(p["id"], today, i)
                variants.append({"name": v["name"], "price": vp, "old_price": vo})
            items.append({
                "id": p["id"], "category": p["category"], "name": p["name"], "description": p["description"],
                "variants": variants,
                "price": price, "old_price": old,
                "discount": round((old - price) * 100 / old) if old else 0,
                "image": p["image"], "badge": p["badge"], "available": p["available"],
            })
        return {"categories": cats, "products": items}

    def public_banners(self) -> list[dict[str, Any]]:
        today = today_local()
        out = []
        for b in self.banners:
            if not banner_active(b, today):
                continue
            link_type, link_id = b["link_type"], b["link_id"]
            if link_type == "product" and not self.is_shown(link_id):
                link_type = ""
            if link_type == "category" and not (self.category(link_id) or {}).get("visible"):
                link_type = ""
            out.append({
                "id": b["id"], "title": _i18n(b["title_uz"], b["title_ru"]), "text": _i18n(b["text_uz"], b["text_ru"]),
                "image": b["image"], "link_type": link_type, "link_id": link_id if link_type else "",
            })
        return out

    def public_store(self) -> dict[str, Any]:
        s = self.store
        return {
            "name": s["name"], "tagline": s["tagline"], "phone": s["phone"], "address": s["address"],
            "location": s["location"], "hours": s["hours"],
            "is_open": self.is_open(), "paused": not s.get("accepting", True),
            "delivery": s["delivery"], "pickup": s["pickup"], "payments": {"cash": True},
            "branches": [{
                "id": b["id"], "name": b["name"], "address": b["address"], "phone": b["phone"],
                "hours": b["hours"], "location": b["location"], "is_open": self.branch_open(b),
            } for b in self.active_branches()],
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

        merged: dict[tuple[str, int | None], int] = {}
        for item in raw_items:
            if not isinstance(item, dict):
                raise OrderError("bad_item")
            pid, qty, v = item.get("id"), item.get("qty"), item.get("v")
            if not isinstance(pid, str) or not self.is_shown(pid):
                raise OrderError("unknown_product", product_id=str(pid))
            if not isinstance(qty, int) or isinstance(qty, bool) or qty < 1:
                raise OrderError("bad_qty")
            variants = self.products[pid]["variants"]
            if variants:
                if not isinstance(v, int) or isinstance(v, bool) or not 0 <= v < len(variants):
                    raise OrderError("bad_variant", product_id=pid)
            elif v not in (None, 0):
                raise OrderError("bad_variant", product_id=pid)
            else:
                v = None
            merged[(pid, v)] = merged.get((pid, v), 0) + qty

        today = today_local()
        lines: list[Line] = []
        for (pid, v), qty in merged.items():
            if qty > MAX_QTY_PER_ITEM:
                raise OrderError("bad_qty")
            if not self.is_available(pid):
                raise OrderError("unavailable", product_id=pid, name=self.products[pid]["name"])
            p = self.products[pid]
            price, _ = self.price_of(pid, today, v)
            name = variant_label(p["name"], p["variants"][v]) if v is not None else p["name"]
            lines.append(Line(product_id=pid, name=name, price=price, qty=qty, variant=v))

        subtotal = sum(line.total for line in lines)
        min_order = int(type_cfg.get("min_order") or 0)
        if subtotal < min_order:
            raise OrderError("min_order", min_order=min_order)
        fee = self.delivery_fee(subtotal, order_type)
        return Quote(lines=lines, subtotal=subtotal, delivery_fee=fee, total=subtotal + fee)
