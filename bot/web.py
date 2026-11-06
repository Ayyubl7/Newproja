"""HTTP server: Mini App sahifasi, uning API'si va Telegram webhook."""
from __future__ import annotations

import logging
import math
import re
import time
from typing import Any

from aiohttp import web
from aiogram.utils.web_app import WebAppUser, safe_parse_webapp_init_data

from .catalog import PAYMENT_METHODS, OrderError
from .config import WEBAPP_DIR
from .context import AppContext, spawn
from .orders import announce_new_order
from .texts import norm_lang

log = logging.getLogger(__name__)

CTX_KEY = web.AppKey("ctx", AppContext)
INIT_DATA_MAX_AGE = 24 * 3600
ORDER_COOLDOWN_SEC = 15
PHONE_RE = re.compile(r"^\+?[0-9][0-9 ()\-]{6,20}$")

_last_order_at: dict[int, float] = {}


class ApiError(Exception):
    """API xatosi — middleware uni JSON javobga aylantiradi."""

    def __init__(self, status: int, code: str, **details: Any) -> None:
        super().__init__(code)
        self.status = status
        self.payload = {"ok": False, "error": code, **details}


def _auth(request: web.Request) -> WebAppUser:
    ctx = request.app[CTX_KEY]
    header = request.headers.get("Authorization", "")
    init_data = header[4:] if header.startswith("tma ") else ""
    if not init_data:
        if ctx.settings.dev_mode:
            return WebAppUser(id=ctx.settings.dev_user_id or 1, first_name="Dev")
        raise ApiError(401, "unauthorized")
    try:
        data = safe_parse_webapp_init_data(ctx.settings.bot_token, init_data)
    except ValueError:
        raise ApiError(401, "unauthorized") from None
    if data.user is None or time.time() - data.auth_date.timestamp() > INIT_DATA_MAX_AGE:
        raise ApiError(401, "unauthorized")
    return data.user


# ---------- API ----------
async def api_bootstrap(request: web.Request) -> web.Response:
    ctx = request.app[CTX_KEY]
    user = _auth(request)
    profile = await ctx.db.get_user(user.id) or {}
    lang = profile.get("lang") or ("ru" if (user.language_code or "").startswith("ru") else "uz")
    return web.json_response({
        "ok": True,
        "store": ctx.catalog.public_store(),
        "menu": ctx.catalog.public_menu(),
        "banners": ctx.catalog.public_banners(),
        "profile": {
            "lang": norm_lang(lang),
            "name": profile.get("first_name") or user.first_name or "",
            "phone": profile.get("phone") or "",
            "address": profile.get("last_address") or "",
        },
    })


def _clean_str(value: Any, max_len: int) -> str:
    if value is None:
        return ""
    if not isinstance(value, str):
        raise ApiError(400, "bad_request")
    value = " ".join(value.split())  # ortiqcha bo'shliq va qator ko'chishlarini olib tashlash
    if len(value) > max_len:
        raise ApiError(400, "too_long")
    return value


def _coord(value: Any, limit: float) -> float | None:
    if value is None or value == "":
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ApiError(400, "bad_location")
    value = float(value)
    if not math.isfinite(value) or abs(value) > limit:
        raise ApiError(400, "bad_location")
    return round(value, 6)


async def api_order(request: web.Request) -> web.Response:
    ctx = request.app[CTX_KEY]
    user = _auth(request)
    try:
        body = await request.json()
    except Exception:
        raise ApiError(400, "bad_request") from None
    if not isinstance(body, dict):
        raise ApiError(400, "bad_request")

    profile = await ctx.db.get_user(user.id) or {}
    lang = norm_lang(body.get("lang") or profile.get("lang"))
    order_type = body.get("type")
    payment = body.get("payment", "cash")
    phone = _clean_str(body.get("phone"), 24)
    name = _clean_str(body.get("name"), 64) or user.first_name or ""
    address = _clean_str(body.get("address"), 300)
    comment = _clean_str(body.get("comment"), 300)
    lat, lon = _coord(body.get("lat"), 90), _coord(body.get("lon"), 180)

    if not ctx.catalog.store.get("accepting", True):
        raise ApiError(409, "paused")
    if not ctx.catalog.is_open():
        raise ApiError(409, "closed")
    if payment not in PAYMENT_METHODS or not ctx.catalog.store.get("payments", {}).get(payment):
        raise ApiError(400, "payment_unavailable")
    if not PHONE_RE.match(phone) or not 9 <= sum(c.isdigit() for c in phone) <= 15:
        raise ApiError(400, "bad_phone")
    if order_type == "delivery":
        if len(address) < 5:
            raise ApiError(400, "bad_address")
        if (lat is None) != (lon is None):
            raise ApiError(400, "bad_location")
    else:
        address, lat, lon = "", None, None

    try:
        quote = ctx.catalog.quote(body.get("items"), order_type)
    except OrderError as e:
        raise ApiError(400, e.code, **e.details) from None

    now = time.monotonic()
    last = _last_order_at.get(user.id)
    if last is not None and now - last < ORDER_COOLDOWN_SEC:
        raise ApiError(429, "too_fast")
    _last_order_at[user.id] = now

    order_id = await ctx.db.create_order({
        "user_id": user.id,
        "items": [line.as_dict() for line in quote.lines],
        "subtotal": quote.subtotal,
        "delivery_fee": quote.delivery_fee,
        "total": quote.total,
        "type": order_type,
        "address": address or None,
        "lat": lat,
        "lon": lon,
        "phone": phone,
        "name": name,
        "comment": comment or None,
        "payment": payment,
        "lang": lang,
    })
    await ctx.db.upsert_user(user.id, profile.get("first_name") or user.first_name, user.username)
    await ctx.db.set_user_field(user.id, "phone", phone)
    if not profile.get("lang"):
        await ctx.db.set_user_field(user.id, "lang", lang)
    if address:
        await ctx.db.set_user_field(user.id, "last_address", address)

    # Telegram'ga yuborish fonda — mijoz javobni darhol oladi
    spawn(announce_new_order(ctx, order_id))
    log.info("Yangi buyurtma #%s: user=%s total=%s", order_id, user.id, quote.total)
    return web.json_response({"ok": True, "order": {"id": order_id, "total": quote.total}})


async def health(_: web.Request) -> web.Response:
    return web.Response(text="ok")


# ---------- statik fayllar ----------
async def index(_: web.Request) -> web.FileResponse:
    return web.FileResponse(WEBAPP_DIR / "index.html", headers={"Cache-Control": "no-cache"})


@web.middleware
async def api_errors(request: web.Request, handler):
    try:
        return await handler(request)
    except ApiError as e:
        return web.json_response(e.payload, status=e.status)


@web.middleware
async def cache_headers(request: web.Request, handler):
    resp = await handler(request)
    if isinstance(resp, web.StreamResponse):
        if request.path.startswith("/static/"):
            resp.headers.setdefault("Cache-Control", "public, max-age=3600")
        elif request.path.startswith("/media/"):
            # Yuklangan rasm nomlari tasodifiy va o'zgarmaydi — uzoq keshlash mumkin
            resp.headers.setdefault("Cache-Control", "public, max-age=2592000, immutable")
    return resp


def build_web_app(ctx: AppContext) -> web.Application:
    app = web.Application(middlewares=[api_errors, cache_headers], client_max_size=64 * 1024)
    app[CTX_KEY] = ctx
    app.router.add_get("/", index)
    app.router.add_get("/health", health)
    app.router.add_get("/api/bootstrap", api_bootstrap)
    app.router.add_post("/api/order", api_order)
    app.router.add_static("/static/", WEBAPP_DIR, show_index=False)
    ctx.settings.upload_dir.mkdir(parents=True, exist_ok=True)
    app.router.add_static("/media/", ctx.settings.upload_dir, show_index=False)

    from .admin_api import setup_admin_routes  # admin_api web.py'dan import qiladi — aylanma importdan qochish
    setup_admin_routes(app)
    return app
