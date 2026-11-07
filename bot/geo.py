"""Koordinatadan manzil matnini olish (OpenStreetMap Nominatim, bepul, kalitsiz).

Nominatim qoidasi: soniyasiga ko'pi bilan 1 so'rov va aniq User-Agent. Bitta restoran uchun bu yetarli.
GEOCODER=off bo'lsa yoki xizmat javob bermasa — None qaytadi va manzil o'rniga koordinata ko'rsatiladi.
"""
from __future__ import annotations

import asyncio
import logging
import os
import time

import aiohttp

log = logging.getLogger(__name__)

_lock = asyncio.Lock()
_last_call = 0.0
_cache: dict[tuple[float, float, str], str] = {}


def _short_address(data: dict) -> str | None:
    a = data.get("address") or {}
    street = a.get("road") or a.get("pedestrian") or a.get("residential") or ""
    if street and a.get("house_number"):
        street = f"{street}, {a['house_number']}"
    area = a.get("neighbourhood") or a.get("quarter") or a.get("suburb") or ""
    city = a.get("city") or a.get("town") or a.get("village") or a.get("county") or ""
    parts = [p for p in (street, area, city) if p]
    # takrorlarni olib tashlash (masalan, mahalla va tuman bir xil bo'lsa)
    uniq = list(dict.fromkeys(parts))
    if uniq:
        return ", ".join(uniq)[:160]
    name = data.get("display_name") or ""
    return name[:160] or None


async def reverse_geocode(lat: float, lon: float, lang: str = "uz", contact: str = "") -> str | None:
    if os.getenv("GEOCODER", "nominatim").lower() in ("off", "0", "none"):
        return None
    key = (round(lat, 4), round(lon, 4), lang)
    if key in _cache:
        return _cache[key]
    global _last_call
    params = {"format": "jsonv2", "lat": f"{lat:.6f}", "lon": f"{lon:.6f}", "zoom": "18",
              "addressdetails": "1", "accept-language": "ru" if lang == "ru" else "uz,ru"}
    headers = {"User-Agent": f"AyvaBurgersBot/1.0 ({contact or 'telegram bot'})"}
    try:
        async with _lock:
            wait = 1.1 - (time.monotonic() - _last_call)
            if wait > 0:
                await asyncio.sleep(wait)
            _last_call = time.monotonic()
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=6)) as s:
                async with s.get("https://nominatim.openstreetmap.org/reverse", params=params, headers=headers) as r:
                    if r.status != 200:
                        return None
                    data = await r.json(content_type=None)
    except Exception as e:  # noqa: BLE001 — manzil bo'lmasa ham buyurtma ishlayveradi
        log.info("Manzilni aniqlab bo'lmadi: %s", e)
        return None
    addr = _short_address(data or {})
    if addr:
        _cache[key] = addr
    return addr


def coords_text(lat: float, lon: float) -> str:
    return f"📍 {lat:.5f}, {lon:.5f}"
