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
            await db.create_product(p["id"], {
                "category_id": p["category"],
                "name_uz": p["name"]["uz"], "name_ru": p["name"].get("ru", ""),
                "desc_uz": (p.get("description") or {}).get("uz", ""),
                "desc_ru": (p.get("description") or {}).get("ru", ""),
                "price": int(p["price"]), "image": p.get("image") or "", "badge": p.get("badge") or "",
                "available": True, "visible": True, "sort": i,
            })
        for pid in await db.pop_legacy_stoplist():
            await db.update_product(pid, {"available": False})
        log.info("Menyu menu.json'dan bazaga yuklandi: %s kategoriya, %s mahsulot",
                 len(menu["categories"]), len(menu["products"]))

    if await db.get_setting("store") is None:
        store = json.loads((data_dir / "store.json").read_text(encoding="utf-8"))
        await db.set_setting("store", store)
        log.info("Do'kon sozlamalari store.json'dan bazaga yuklandi")
