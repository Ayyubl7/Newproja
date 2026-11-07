"""Birinchi ishga tushishda menyu va sozlamalarni data/*.json fayllaridan bazaga yuklash.

Shundan keyin menyu faqat admin paneldan boshqariladi — JSON fayllar qayta o'qilmaydi.
"""
from __future__ import annotations

import json
import logging
from pathlib import Path

from .db import Database

log = logging.getLogger(__name__)


async def ensure_seeded(db: Database, data_dir: Path) -> None:
    if not await db.list_categories():
        menu = json.loads((data_dir / "menu.json").read_text(encoding="utf-8"))
        for i, c in enumerate(menu["categories"]):
            await db.create_category(c["id"], {
                "name_uz": c["name"]["uz"], "name_ru": c["name"].get("ru", ""),
                "icon": c.get("icon", "burger"), "sort": i, "visible": True,
            })
        for i, p in enumerate(menu["products"]):
            variants = p.get("variants") or []
            await db.create_product(p["id"], {
                "variants": variants,
                "category_id": p["category"],
                "name_uz": p["name"]["uz"], "name_ru": p["name"].get("ru", ""),
                "desc_uz": (p.get("description") or {}).get("uz", ""),
                "desc_ru": (p.get("description") or {}).get("ru", ""),
                "price": min(v["price"] for v in variants) if variants else int(p["price"]),
                "image": p.get("image") or "", "badge": p.get("badge") or "",
                "available": True, "visible": True, "sort": i,
            })
        for pid in await db.pop_legacy_stoplist():
            await db.update_product(pid, {"available": False})
        log.info("Menyu menu.json'dan bazaga yuklandi: %s kategoriya, %s mahsulot",
                 len(menu["categories"]), len(menu["products"]))

    store_file = json.loads((data_dir / "store.json").read_text(encoding="utf-8"))
    if await db.get_setting("store") is None:
        await db.set_setting("store", {k: v for k, v in store_file.items() if k != "branches"})
        log.info("Do'kon sozlamalari store.json'dan bazaga yuklandi")

    if not await db.list_branches():
        store = await db.get_setting("store") or {}
        branches = store_file.get("branches") or [{
            # filiallar ko'rsatilmagan bo'lsa — bitta asosiy filial do'kon ma'lumotlaridan
            "id": "main", "name": {"uz": store.get("name", "Asosiy"), "ru": store.get("name", "Основной")},
            "address": store.get("address") or {}, "phone": store.get("phone", ""),
            "hours": store.get("hours") or {"open": "00:00", "close": "00:00"}, "location": store.get("location"),
        }]
        for i, b in enumerate(branches):
            loc = b.get("location") or {}
            await db.create_branch(b["id"], {
                "name_uz": b["name"]["uz"], "name_ru": b["name"].get("ru", ""),
                "address_uz": (b.get("address") or {}).get("uz", ""), "address_ru": (b.get("address") or {}).get("ru", ""),
                "phone": b.get("phone", ""), "open": b["hours"]["open"], "close": b["hours"]["close"],
                "lat": loc.get("lat"), "lon": loc.get("lon"), "chat_id": b.get("chat_id"),
                "active": True, "sort": i,
            })
        log.info("Filiallar bazaga yuklandi: %s ta", len(branches))
