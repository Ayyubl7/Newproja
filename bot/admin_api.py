"""Admin panel API (/api/admin/*) va kirish.

Kirish ikki yo'l bilan:
  * Telegram ichida — Mini App initData imzosi (Authorization: tma ...)
  * Kompyuterda — botdagi bir martalik havola orqali olingan imzolangan cookie (7 kun)
Ikkala holatda ham foydalanuvchi ADMIN_IDS (egalar) yoki paneldan qo'shilgan adminlar ichida bo'lishi shart.
"""
from __future__ import annotations

import asyncio
import hashlib
import hmac
import json
import logging
import math
import re
import secrets
import time
import uuid
from collections.abc import Awaitable, Callable
from datetime import date, timedelta
from io import BytesIO
from typing import Any

from aiogram.types import FSInputFile, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from aiogram.utils.web_app import safe_parse_webapp_init_data
from aiohttp import web
from PIL import Image, ImageOps

from .broadcast import start_broadcast
from .catalog import (
    BADGES,
    ICONS,
    MAX_VARIANTS,
    parse_variants,
    _merge,
    banner_active,
    normalize_store,
    promo_active,
    today_local,
)
from .config import WEBAPP_DIR
from .context import FULL_ROLES, ROLES, AppContext, spawn
from .db import days_ago_utc, local_time
from .keyboards import webapp_url
from .orders import ACTIVE_STATUSES, apply_status, notify_user_status, sync_admin_message
from .texts import t
from .web import CTX_KEY, INIT_DATA_MAX_AGE, ApiError

log = logging.getLogger(__name__)

COOKIE = "ayva_admin"
SESSION_DAYS = 7
MAX_UPLOAD = 12 * 1024 * 1024
IMAGE_MAX_SIDE = 1200
Image.MAX_IMAGE_PIXELS = 40_000_000  # "decompression bomb" himoyasi
MEDIA_RE = re.compile(r"^/media/[0-9a-f]{32}\.webp$")
LEGACY_IMG_RE = re.compile(r"^img/[\w\-/]+\.(png|jpe?g|webp|svg)$")
HHMM_RE = re.compile(r"^([01]\d|2[0-3]):[0-5]\d$")
USERNAME_RE = re.compile(r"^[A-Za-z0-9_]{0,40}$")

Handler = Callable[[web.Request, AppContext], Awaitable[web.StreamResponse]]

# So'rov ichida admin ma'lumotini saqlash kalitlari (eski aiohttp'da oddiy satr)
_RK = getattr(web, "RequestKey", None)
ADMIN_ID: Any = _RK("admin_id", int) if _RK else "admin_id"
ADMIN_NAME: Any = _RK("admin_name", str) if _RK else "admin_name"
IS_OWNER: Any = _RK("is_owner", bool) if _RK else "is_owner"
ROLE: Any = _RK("role", str) if _RK else "role"

# Kassir o'zgartira oladigan maydonlar
CASHIER_PRODUCT_FIELDS = {"available"}
CASHIER_STORE_FIELDS = {"accepting"}


# =====================================================================  kirish
def _session_key(ctx: AppContext) -> bytes:
    return hashlib.sha256(b"ayva-admin-session:" + ctx.settings.bot_token.encode()).digest()


def make_session(ctx: AppContext, user_id: int) -> str:
    payload = f"{user_id}.{int(time.time()) + SESSION_DAYS * 86400}"
    sig = hmac.new(_session_key(ctx), payload.encode(), hashlib.sha256).hexdigest()
    return f"{payload}.{sig}"


def read_session(ctx: AppContext, value: str) -> int | None:
    try:
        uid, exp, sig = value.split(".")
        expected = hmac.new(_session_key(ctx), f"{uid}.{exp}".encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(sig, expected) or int(exp) < time.time():
            return None
        return int(uid)
    except (ValueError, AttributeError):
        return None


def _authenticate(request: web.Request) -> tuple[int, str, str]:
    """(user_id, ism, rol). Xato bo'lsa ApiError."""
    ctx = request.app[CTX_KEY]
    header = request.headers.get("Authorization", "")
    uid: int | None = None
    name = ""
    if header.startswith("tma "):
        try:
            data = safe_parse_webapp_init_data(ctx.settings.bot_token, header[4:])
        except ValueError:
            raise ApiError(401, "unauthorized") from None
        if data.user is None or time.time() - data.auth_date.timestamp() > INIT_DATA_MAX_AGE:
            raise ApiError(401, "unauthorized")
        uid, name = data.user.id, data.user.first_name or ""
    elif request.cookies.get(COOKIE):
        uid = read_session(ctx, request.cookies[COOKIE])
        # Cookie bilan kelgan o'zgartirish so'rovlarida maxsus sarlavha shart (CSRF himoyasi)
        if uid is not None and request.method != "GET" and request.headers.get("X-Admin") != "1":
            raise ApiError(403, "csrf")
    if uid is None:
        if ctx.settings.dev_mode:
            return ctx.settings.dev_user_id or 1, "Dev", "owner"
        raise ApiError(401, "unauthorized")
    role = ctx.role_of(uid)
    if role is None:
        raise ApiError(403, "forbidden", user_id=uid)
    return uid, name, role


def admin_route(handler: Handler | None = None, *, cashier: bool = False):
    """Admin API marshruti. Standart holatda kassirga yopiq; cashier=True — kassir ham kira oladi."""
    def decorate(fn: Handler) -> Callable[[web.Request], Awaitable[web.StreamResponse]]:
        async def wrapper(request: web.Request) -> web.StreamResponse:
            uid, name, role = _authenticate(request)
            if role not in FULL_ROLES and not cashier:
                raise ApiError(403, "role_forbidden")
            request[ADMIN_ID], request[ADMIN_NAME], request[ROLE] = uid, name, role
            request[IS_OWNER] = role == "owner"
            return await fn(request, request.app[CTX_KEY])
        return wrapper
    return decorate(handler) if handler is not None else decorate


def _cashier_only(request: web.Request, body: dict[str, Any], allowed: set[str]) -> None:
    if request[ROLE] not in FULL_ROLES and not set(body) <= allowed:
        raise ApiError(403, "role_forbidden")


async def _admin_display_name(request: web.Request, ctx: AppContext) -> str:
    if request.get(ADMIN_NAME):
        return request[ADMIN_NAME]
    user = await ctx.db.get_user(request[ADMIN_ID])
    return (user or {}).get("first_name") or "Admin"


async def login(request: web.Request) -> web.Response:
    ctx = request.app[CTX_KEY]
    uid = ctx.use_login_token(request.query.get("t", ""))
    if uid is None or not ctx.is_panel_admin(uid):
        raise web.HTTPFound("/admin/?login=expired")
    resp = web.HTTPFound("/admin/")
    resp.set_cookie(COOKIE, make_session(ctx, uid), max_age=SESSION_DAYS * 86400, httponly=True,
                    secure=request.secure or ctx.settings.public_url.startswith("https://"),
                    samesite="Strict", path="/")
    raise resp


async def logout(request: web.Request) -> web.Response:
    resp = web.json_response({"ok": True})
    resp.del_cookie(COOKIE, path="/")
    return resp


async def admin_redirect(_: web.Request) -> web.Response:
    raise web.HTTPFound("/admin/")


async def admin_index(_: web.Request) -> web.FileResponse:
    return web.FileResponse(WEBAPP_DIR / "admin" / "index.html", headers={"Cache-Control": "no-cache"})


# =====================================================================  tekshiruvlar
def _bad(field: str, code: str = "invalid") -> ApiError:
    return ApiError(400, code, field=field)


def v_str(body: dict, key: str, max_len: int, required: bool = False) -> str:
    v = body.get(key, "")
    if v is None:
        v = ""
    if not isinstance(v, str):
        raise _bad(key)
    v = v.strip()
    if required and not v:
        raise _bad(key, "required")
    if len(v) > max_len:
        raise _bad(key, "too_long")
    return v


def v_int(body: dict, key: str, lo: int, hi: int, nullable: bool = False) -> int | None:
    v = body.get(key)
    if v is None or v == "":
        if nullable:
            return None
        raise _bad(key, "required")
    if isinstance(v, bool) or not isinstance(v, (int, float)) or (isinstance(v, float) and not v.is_integer()):
        raise _bad(key)
    v = int(v)
    if not lo <= v <= hi:
        raise _bad(key, "out_of_range")
    return v


def v_bool(body: dict, key: str) -> bool:
    v = body.get(key)
    if not isinstance(v, bool):
        raise _bad(key)
    return v


def v_date(body: dict, key: str) -> str | None:
    v = body.get(key)
    if v in (None, ""):
        return None
    try:
        return date.fromisoformat(v).isoformat()
    except (TypeError, ValueError):
        raise _bad(key) from None


def v_choice(body: dict, key: str, choices: tuple[str, ...]) -> str:
    v = body.get(key, "")
    if v not in choices:
        raise _bad(key)
    return v


def v_image(body: dict, key: str = "image") -> str:
    v = body.get(key) or ""
    if not isinstance(v, str) or (v and not MEDIA_RE.match(v) and not LEGACY_IMG_RE.match(v)):
        raise _bad(key)
    return v


def v_ids(body: dict, key: str = "ids") -> list:
    v = body.get(key)
    if not isinstance(v, list) or len(v) > 500:
        raise _bad(key)
    return v


async def _json(request: web.Request) -> dict[str, Any]:
    try:
        body = await request.json()
    except Exception:
        raise ApiError(400, "bad_request") from None
    if not isinstance(body, dict):
        raise ApiError(400, "bad_request")
    return body


def ok(**data: Any) -> web.Response:
    return web.json_response({"ok": True, **data})


async def _drop_image_if_unused(ctx: AppContext, image: str) -> None:
    if image and MEDIA_RE.match(image) and not await ctx.db.image_in_use(image):
        try:
            (ctx.settings.upload_dir / image.rsplit("/", 1)[1]).unlink(missing_ok=True)
        except OSError:
            log.warning("Rasmni o'chirib bo'lmadi: %s", image)


# =====================================================================  profil
@admin_route(cashier=True)
async def me(request: web.Request, ctx: AppContext) -> web.Response:
    return ok(user={"id": request[ADMIN_ID], "name": await _admin_display_name(request, ctx)},
              is_owner=request[IS_OWNER], role=request[ROLE], lang=ctx.settings.admin_lang,
              store_name=ctx.catalog.store.get("name", ""))


# =====================================================================  rasm yuklash
def _process_image(data: bytes, upload_dir) -> str:
    try:
        im = Image.open(BytesIO(data))
        im.load()
    except Exception:
        raise ApiError(400, "bad_image") from None
    im = ImageOps.exif_transpose(im)
    has_alpha = im.mode in ("RGBA", "LA") or (im.mode == "P" and "transparency" in im.info)
    im = im.convert("RGBA" if has_alpha else "RGB")
    im.thumbnail((IMAGE_MAX_SIDE, IMAGE_MAX_SIDE), Image.Resampling.LANCZOS)
    upload_dir.mkdir(parents=True, exist_ok=True)
    name = uuid.uuid4().hex + ".webp"
    im.save(upload_dir / name, "WEBP", quality=82, method=4)
    return name


@admin_route
async def upload(request: web.Request, ctx: AppContext) -> web.Response:
    try:
        reader = await request.multipart()
    except Exception:
        raise ApiError(400, "bad_request") from None
    part = await reader.next()
    while part is not None and getattr(part, "name", None) != "file":
        part = await reader.next()
    if part is None:
        raise ApiError(400, "no_file")
    buf, size = BytesIO(), 0
    while chunk := await part.read_chunk(256 * 1024):
        size += len(chunk)
        if size > MAX_UPLOAD:
            raise ApiError(413, "too_large")
        buf.write(chunk)
    name = await asyncio.to_thread(_process_image, buf.getvalue(), ctx.settings.upload_dir)
    return ok(url=f"/media/{name}")


# =====================================================================  menyu
def _promo_state(p: dict[str, Any], today: date) -> str:
    if not p.get("promo_price"):
        return ""
    if promo_active(p, today):
        return "active"
    if p.get("promo_from") and today < date.fromisoformat(p["promo_from"]):
        return "scheduled"
    return "expired"


@admin_route(cashier=True)
async def get_menu(request: web.Request, ctx: AppContext) -> web.Response:
    today = today_local()
    products = []
    for r in await ctx.db.list_products():
        r = dict(r)
        r["available"], r["visible"] = bool(r["available"]), bool(r["visible"])
        r["variants"] = [{"uz": v["name"]["uz"], "ru": v["name"]["ru"] if v["name"]["ru"] != v["name"]["uz"] else "",
                          "price": v["price"]} for v in parse_variants(r.get("variants"))]
        r["promo_state"] = _promo_state(r, today)
        products.append(r)
    cats = [{**c, "visible": bool(c["visible"])} for c in await ctx.db.list_categories()]
    return ok(categories=cats, products=products, icons=list(ICONS), badges=list(BADGES))


def _parse_category(body: dict, partial: bool) -> dict[str, Any]:
    out: dict[str, Any] = {}
    if not partial or "name_uz" in body:
        out["name_uz"] = v_str(body, "name_uz", 40, required=True)
    if "name_ru" in body:
        out["name_ru"] = v_str(body, "name_ru", 40)
    if "icon" in body:
        out["icon"] = v_choice(body, "icon", ICONS)
    if "visible" in body:
        out["visible"] = v_bool(body, "visible")
    return out


@admin_route
async def create_category(request: web.Request, ctx: AppContext) -> web.Response:
    data = _parse_category(await _json(request), partial=False)
    cat_id = "c" + secrets.token_hex(3)
    await ctx.db.create_category(cat_id, data)
    await ctx.reload_catalog()
    return ok(category=await ctx.db.get_category(cat_id))


@admin_route
async def update_category(request: web.Request, ctx: AppContext) -> web.Response:
    cat_id = request.match_info["id"]
    if not await ctx.db.get_category(cat_id):
        raise ApiError(404, "not_found")
    await ctx.db.update_category(cat_id, _parse_category(await _json(request), partial=True))
    await ctx.reload_catalog()
    return ok(category=await ctx.db.get_category(cat_id))


@admin_route
async def delete_category(request: web.Request, ctx: AppContext) -> web.Response:
    cat_id = request.match_info["id"]
    if not await ctx.db.get_category(cat_id):
        raise ApiError(404, "not_found")
    if await ctx.db.count_products_in(cat_id):
        raise ApiError(409, "category_not_empty")
    await ctx.db.delete_category(cat_id)
    await ctx.reload_catalog()
    return ok()


def v_variants(body: dict) -> list[dict[str, Any]]:
    raw = body.get("variants")
    if raw in (None, ""):
        return []
    if not isinstance(raw, list) or len(raw) > MAX_VARIANTS:
        raise _bad("variants")
    out = []
    for item in raw:
        if not isinstance(item, dict):
            raise _bad("variants")
        out.append({"uz": v_str(item, "uz", 30, required=True), "ru": v_str(item, "ru", 30),
                    "price": v_int(item, "price", 100, 100_000_000)})
    return out


def _parse_product(body: dict, partial: bool) -> dict[str, Any]:
    out: dict[str, Any] = {}
    if "variants" in body:
        out["variants"] = v_variants(body)
    if not partial or "name_uz" in body:
        out["name_uz"] = v_str(body, "name_uz", 80, required=True)
    if out.get("variants"):
        out["price"] = min(v["price"] for v in out["variants"])  # asosiy narx = eng arzon variant
    elif not partial or "price" in body:
        out["price"] = v_int(body, "price", 100, 100_000_000)
    if not partial or "category_id" in body:
        out["category_id"] = v_str(body, "category_id", 40, required=True)
    for key, n in (("name_ru", 80), ("desc_uz", 300), ("desc_ru", 300)):
        if key in body:
            out[key] = v_str(body, key, n)
    if "promo_price" in body:
        out["promo_price"] = v_int(body, "promo_price", 0, 100_000_000, nullable=True) or None
    for key in ("promo_from", "promo_to"):
        if key in body:
            out[key] = v_date(body, key)
    if "image" in body:
        out["image"] = v_image(body)
    if "badge" in body:
        out["badge"] = v_choice(body, "badge", BADGES)
    for key in ("available", "visible"):
        if key in body:
            out[key] = v_bool(body, key)
    return out


async def _check_product(ctx: AppContext, merged: dict[str, Any]) -> None:
    variants = merged.get("variants")
    if isinstance(variants, str):
        variants = json.loads(variants)
    if variants:
        merged["price"] = min(v["price"] for v in variants)
    if not await ctx.db.get_category(merged["category_id"]):
        raise _bad("category_id")
    if merged.get("promo_price") is not None and merged["promo_price"] >= merged["price"]:
        raise _bad("promo_price", "promo_not_lower")
    if merged.get("promo_from") and merged.get("promo_to") and merged["promo_from"] > merged["promo_to"]:
        raise _bad("promo_to", "bad_range")


@admin_route
async def create_product(request: web.Request, ctx: AppContext) -> web.Response:
    data = _parse_product(await _json(request), partial=False)
    await _check_product(ctx, data)
    pid = "p" + secrets.token_hex(4)
    await ctx.db.create_product(pid, data)
    await ctx.reload_catalog()
    return ok(product=await ctx.db.get_product(pid))


@admin_route(cashier=True)
async def update_product(request: web.Request, ctx: AppContext) -> web.Response:
    pid = request.match_info["id"]
    body = await _json(request)
    _cashier_only(request, body, CASHIER_PRODUCT_FIELDS)  # kassir faqat stop-list
    current = await ctx.db.get_product(pid)
    if not current:
        raise ApiError(404, "not_found")
    data = _parse_product(body, partial=True)
    merged = {**current, **data}
    await _check_product(ctx, merged)
    if merged.get("variants") and "price" not in data:
        data["price"] = merged["price"]
    await ctx.db.update_product(pid, data)
    if "image" in data and data["image"] != current["image"]:
        await _drop_image_if_unused(ctx, current["image"])
    await ctx.reload_catalog()
    return ok(product=await ctx.db.get_product(pid))


@admin_route
async def delete_product(request: web.Request, ctx: AppContext) -> web.Response:
    pid = request.match_info["id"]
    current = await ctx.db.get_product(pid)
    if not current:
        raise ApiError(404, "not_found")
    await ctx.db.delete_product(pid)
    await _drop_image_if_unused(ctx, current["image"])
    await ctx.reload_catalog()
    return ok()


def _reorder(table: str, exists: Callable[[Any], Awaitable[Any]]) -> Handler:
    async def handler(request: web.Request, ctx: AppContext) -> web.Response:
        ids = v_ids(await _json(request))
        for i in ids:
            if not isinstance(i, (str, int)) or isinstance(i, bool) or not await exists(ctx, i):
                raise _bad("ids")
        await ctx.db.reorder(table, ids)
        await ctx.reload_catalog()
        return ok()
    return handler


reorder_categories = admin_route(_reorder("categories", lambda ctx, i: ctx.db.get_category(str(i))))
reorder_products = admin_route(_reorder("products", lambda ctx, i: ctx.db.get_product(str(i))))


async def _banner_exists(ctx: AppContext, banner_id: Any) -> bool:
    return str(banner_id).isdigit() and await ctx.db.get_banner(int(banner_id)) is not None


reorder_banners = admin_route(_reorder("banners", _banner_exists))


# =====================================================================  bannerlar (aksiyalar)
def _banner_out(b: dict[str, Any], today: date) -> dict[str, Any]:
    state = "active" if banner_active(b, today) else ("off" if not b["active"] else (
        "scheduled" if b.get("date_from") and today < date.fromisoformat(b["date_from"]) else "expired"))
    return {**b, "active": bool(b["active"]), "state": state}


@admin_route
async def get_banners(request: web.Request, ctx: AppContext) -> web.Response:
    today = today_local()
    return ok(banners=[_banner_out(b, today) for b in await ctx.db.list_banners()])


def _parse_banner(body: dict, partial: bool) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for key, n in (("title_uz", 60), ("title_ru", 60), ("text_uz", 140), ("text_ru", 140)):
        if not partial or key in body:
            out[key] = v_str(body, key, n)
    if not partial or "image" in body:
        out["image"] = v_image(body)
    if not partial or "link_type" in body:
        out["link_type"] = v_choice(body, "link_type", ("", "product", "category"))
        out["link_id"] = v_str(body, "link_id", 40) if out["link_type"] else ""
    for key in ("date_from", "date_to"):
        if not partial or key in body:
            out[key] = v_date(body, key)
    if "active" in body:
        out["active"] = v_bool(body, "active")
    return out


async def _check_banner(ctx: AppContext, b: dict[str, Any]) -> None:
    if not b.get("title_uz") and not b.get("image"):
        raise _bad("title_uz", "title_or_image")
    if b.get("link_type") == "product" and not await ctx.db.get_product(b["link_id"]):
        raise _bad("link_id")
    if b.get("link_type") == "category" and not await ctx.db.get_category(b["link_id"]):
        raise _bad("link_id")
    if b.get("date_from") and b.get("date_to") and b["date_from"] > b["date_to"]:
        raise _bad("date_to", "bad_range")


@admin_route
async def create_banner(request: web.Request, ctx: AppContext) -> web.Response:
    data = _parse_banner(await _json(request), partial=False)
    data.setdefault("active", True)
    await _check_banner(ctx, data)
    bid = await ctx.db.create_banner(data)
    await ctx.reload_catalog()
    return ok(banner=_banner_out(await ctx.db.get_banner(bid), today_local()))


def _banner_id(request: web.Request) -> int:
    raw = request.match_info["id"]
    if not raw.isdigit():
        raise ApiError(404, "not_found")
    return int(raw)


@admin_route
async def update_banner(request: web.Request, ctx: AppContext) -> web.Response:
    bid = _banner_id(request)
    current = await ctx.db.get_banner(bid)
    if not current:
        raise ApiError(404, "not_found")
    data = _parse_banner(await _json(request), partial=True)
    await _check_banner(ctx, {**current, **data})
    await ctx.db.update_banner(bid, data)
    if "image" in data and data["image"] != current["image"]:
        await _drop_image_if_unused(ctx, current["image"])
    await ctx.reload_catalog()
    return ok(banner=_banner_out(await ctx.db.get_banner(bid), today_local()))


@admin_route
async def delete_banner(request: web.Request, ctx: AppContext) -> web.Response:
    bid = _banner_id(request)
    current = await ctx.db.get_banner(bid)
    if not current:
        raise ApiError(404, "not_found")
    await ctx.db.delete_banner(bid)
    await _drop_image_if_unused(ctx, current["image"])
    await ctx.reload_catalog()
    return ok()


# =====================================================================  do'kon sozlamalari
def _validate_store(s: dict[str, Any]) -> dict[str, Any]:
    def i18n(key: str, n: int) -> dict[str, str]:
        v = s.get(key) or {}
        if not isinstance(v, dict):
            raise _bad(key)
        return {"uz": v_str(v, "uz", n), "ru": v_str(v, "ru", n)}

    out: dict[str, Any] = {
        "name": v_str(s, "name", 60, required=True),
        "tagline": i18n("tagline", 120),
        "about": i18n("about", 600),
        "phone": v_str(s, "phone", 30),
        "support_username": v_str(s, "support_username", 41).lstrip("@"),
        "instagram": v_str(s, "instagram", 60).lstrip("@"),
        "address": i18n("address", 200),
        "accepting": v_bool(s, "accepting"),
    }
    if not USERNAME_RE.match(out["support_username"]):
        raise _bad("support_username")

    loc = s.get("location")
    if loc in (None, "", {}):
        out["location"] = None
    else:
        if not isinstance(loc, dict):
            raise _bad("location")
        lat, lon = loc.get("lat"), loc.get("lon")
        for v in (lat, lon):
            if isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v):
                raise _bad("location")
        if not (-90 <= lat <= 90 and -180 <= lon <= 180):
            raise _bad("location")
        out["location"] = {"lat": round(float(lat), 6), "lon": round(float(lon), 6)}

    hours = s.get("hours") or {}
    if not isinstance(hours, dict) or not HHMM_RE.match(str(hours.get("open", ""))) \
            or not HHMM_RE.match(str(hours.get("close", ""))):
        raise _bad("hours")
    out["hours"] = {"open": hours["open"], "close": hours["close"]}

    d = s.get("delivery") or {}
    p = s.get("pickup") or {}
    if not isinstance(d, dict) or not isinstance(p, dict):
        raise _bad("delivery")
    out["delivery"] = {
        "enabled": v_bool(d, "enabled"),
        "fee": v_int(d, "fee", 0, 10_000_000),
        "free_from": v_int(d, "free_from", 0, 100_000_000),
        "min_order": v_int(d, "min_order", 0, 100_000_000),
        "eta": v_str(d, "eta", 20),
    }
    out["pickup"] = {
        "enabled": v_bool(p, "enabled"),
        "min_order": v_int(p, "min_order", 0, 100_000_000),
        "eta": v_str(p, "eta", 20),
    }
    if not out["delivery"]["enabled"] and not out["pickup"]["enabled"]:
        raise _bad("delivery", "need_one_type")
    out["payments"] = {"cash": True}  # faqat naqd pul
    return out


@admin_route(cashier=True)
async def get_store(request: web.Request, ctx: AppContext) -> web.Response:
    return ok(store=ctx.catalog.store)


@admin_route(cashier=True)
async def patch_store(request: web.Request, ctx: AppContext) -> web.Response:
    body = await _json(request)
    _cashier_only(request, body, CASHIER_STORE_FIELDS)  # kassir faqat buyurtmani to'xtatadi/yoqadi
    merged = _merge(ctx.catalog.store, body)
    store = _validate_store(normalize_store(merged))
    await ctx.db.set_setting("store", store)
    await ctx.reload_catalog()
    return ok(store=ctx.catalog.store)


# =====================================================================  filiallar
def v_coords(body: dict) -> tuple[float | None, float | None]:
    lat, lon = body.get("lat"), body.get("lon")
    if lat in (None, "") and lon in (None, ""):
        return None, None
    for v in (lat, lon):
        if isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v):
            raise _bad("location")
    if not (-90 <= lat <= 90 and -180 <= lon <= 180):
        raise _bad("location")
    return round(float(lat), 6), round(float(lon), 6)


def _parse_branch(body: dict, partial: bool) -> dict[str, Any]:
    out: dict[str, Any] = {}
    if not partial or "name_uz" in body:
        out["name_uz"] = v_str(body, "name_uz", 40, required=True)
    for key, n in (("name_ru", 40), ("address_uz", 200), ("address_ru", 200), ("phone", 30)):
        if key in body:
            out[key] = v_str(body, key, n)
    for key in ("open", "close"):
        if key in body:
            if not HHMM_RE.match(str(body[key] or "")):
                raise _bad(key)
            out[key] = body[key]
    if "lat" in body or "lon" in body:
        out["lat"], out["lon"] = v_coords(body)
    if "chat_id" in body:
        out["chat_id"] = v_int(body, "chat_id", -(10 ** 15), 10 ** 15, nullable=True) or None
    if "active" in body:
        out["active"] = v_bool(body, "active")
    return out


def _branch_out(ctx: AppContext, r: dict[str, Any]) -> dict[str, Any]:
    b = {**r, "active": bool(r["active"])}
    b["is_open"] = ctx.catalog.branch_open({"hours": {"open": r["open"], "close": r["close"]}})
    return b


@admin_route(cashier=True)
async def list_branches(request: web.Request, ctx: AppContext) -> web.Response:
    return ok(branches=[_branch_out(ctx, r) for r in await ctx.db.list_branches()])


@admin_route
async def create_branch(request: web.Request, ctx: AppContext) -> web.Response:
    data = _parse_branch(await _json(request), partial=False)
    branch_id = "b" + secrets.token_hex(3)
    await ctx.db.create_branch(branch_id, data)
    await ctx.reload_catalog()
    return ok(branch=_branch_out(ctx, await ctx.db.get_branch(branch_id)))


@admin_route
async def update_branch(request: web.Request, ctx: AppContext) -> web.Response:
    branch_id = request.match_info["id"]
    if not await ctx.db.get_branch(branch_id):
        raise ApiError(404, "not_found")
    await ctx.db.update_branch(branch_id, _parse_branch(await _json(request), partial=True))
    await ctx.reload_catalog()
    return ok(branch=_branch_out(ctx, await ctx.db.get_branch(branch_id)))


@admin_route
async def delete_branch(request: web.Request, ctx: AppContext) -> web.Response:
    branch_id = request.match_info["id"]
    if not await ctx.db.get_branch(branch_id):
        raise ApiError(404, "not_found")
    if await ctx.db.active_orders(branch_id):
        raise ApiError(409, "branch_has_orders")
    await ctx.db.delete_branch(branch_id)
    await ctx.reload_catalog()
    return ok()


reorder_branches = admin_route(_reorder("branches", lambda ctx, i: ctx.db.get_branch(str(i))))


# =====================================================================  buyurtmalar
def _order_out(o: dict[str, Any], users: dict[int, dict[str, Any]], ctx: AppContext) -> dict[str, Any]:
    u = users.get(o["user_id"]) or {}
    branch = ctx.catalog.branch(o.get("branch_id"))
    return {
        "branch_id": o.get("branch_id"), "branch": branch["name"] if branch else None,
        "rating": o.get("rating"), "feedback": o.get("feedback") or "",
        "id": o["id"], "status": o["status"], "type": o["type"], "items": o["items"],
        "subtotal": o["subtotal"], "delivery_fee": o["delivery_fee"], "total": o["total"],
        "address": o["address"], "lat": o["lat"], "lon": o["lon"], "phone": o["phone"], "name": o["name"],
        "comment": o["comment"], "payment": o["payment"], "user_id": o["user_id"],
        "username": u.get("username") or "",
        "created_at": o["created_at"], "time": local_time(o["created_at"]).strftime("%H:%M"),
        "date": local_time(o["created_at"]).strftime("%d.%m.%Y"),
    }


@admin_route(cashier=True)
async def list_orders(request: web.Request, ctx: AppContext) -> web.Response:
    tab = request.query.get("tab", "active")
    q = request.query.get("q", "").strip()[:40]
    before = request.query.get("before", "")
    branch = request.query.get("branch", "")[:20] or None
    if tab == "active" and not q:
        orders, more = await ctx.db.active_orders(branch), False
    else:
        statuses = {
            "active": ACTIVE_STATUSES, "done": ("done",), "cancelled": ("cancelled",),
        }.get(tab, ("done", "cancelled") if not q else ACTIVE_STATUSES + ("done", "cancelled"))
        orders = await ctx.db.search_orders(statuses, q, int(before) if before.isdigit() else None, limit=31,
                                            branch_id=branch)
        more = len(orders) > 30
        orders = orders[:30]
    users = await ctx.db.users_by_ids(list({o["user_id"] for o in orders}))
    return ok(orders=[_order_out(o, users, ctx) for o in orders], has_more=more)


@admin_route(cashier=True)
async def set_order_status(request: web.Request, ctx: AppContext) -> web.Response:
    raw = request.match_info["id"]
    if not raw.isdigit():
        raise ApiError(404, "not_found")
    status = v_choice(await _json(request), "status", ("accepted", "on_the_way", "ready", "done", "cancelled"))
    success, order = await apply_status(ctx, int(raw), status)
    if order is None:
        raise ApiError(404, "not_found")
    users = await ctx.db.users_by_ids([order["user_id"]])
    if not success:
        raise ApiError(409, "stale", order=_order_out(order, users, ctx))
    by = await _admin_display_name(request, ctx)
    spawn(sync_admin_message(ctx, order, by))
    spawn(notify_user_status(ctx, order))
    return ok(order=_order_out(order, users, ctx))


# =====================================================================  statistika
@admin_route
async def stats(request: web.Request, ctx: AppContext) -> web.Response:
    days = request.query.get("days", "7")
    days = int(days) if days in ("1", "7", "30") else 7
    since = days_ago_utc(days - 1)
    orders = await ctx.db.orders_since(since)
    first_day = today_local() - timedelta(days=days - 1)
    daily = {(first_day + timedelta(days=i)).isoformat(): {"orders": 0, "revenue": 0} for i in range(days)}

    done = [o for o in orders if o["status"] == "done"]
    for o in orders:
        key = local_time(o["created_at"]).date().isoformat()
        if key in daily and o["status"] != "cancelled":
            daily[key]["orders"] += 1
        if key in daily and o["status"] == "done":
            daily[key]["revenue"] += o["total"]

    top: dict[str, dict[str, Any]] = {}
    for o in done:
        for it in o["items"]:
            key = f'{it["id"]}:{it.get("v", "")}'
            row = top.setdefault(key, {"id": it["id"], "name": it["name"], "qty": 0, "revenue": 0})
            row["qty"] += it["qty"]
            row["revenue"] += it["price"] * it["qty"]
    revenue = sum(o["total"] for o in done)
    hours: dict[int, int] = {}
    for o in orders:
        if o["status"] != "cancelled":
            h = local_time(o["created_at"]).hour
            hours[h] = hours.get(h, 0) + 1

    rated = [o for o in orders if o.get("rating")]
    by_branch: dict[str, dict[str, Any]] = {}
    for o in orders:
        if o["status"] == "cancelled":
            continue
        row = by_branch.setdefault(o.get("branch_id") or "", {"orders": 0, "revenue": 0, "ratings": []})
        row["orders"] += 1
        if o["status"] == "done":
            row["revenue"] += o["total"]
        if o.get("rating"):
            row["ratings"].append(o["rating"])
    branches = []
    for bid, row in by_branch.items():
        b = ctx.catalog.branch(bid)
        branches.append({
            "id": bid, "name": b["name"] if b else None, "orders": row["orders"], "revenue": row["revenue"],
            "rating": round(sum(row["ratings"]) / len(row["ratings"]), 1) if row["ratings"] else None,
        })
    reviews = [{
        "id": o["id"], "rating": o["rating"], "feedback": o.get("feedback") or "", "name": o.get("name") or "",
        "date": local_time(o["created_at"]).strftime("%d.%m %H:%M"),
    } for o in sorted(rated, key=lambda o: -o["id"])[:10]]

    return ok(
        days=days,
        rating={
            "avg": round(sum(o["rating"] for o in rated) / len(rated), 1) if rated else None,
            "count": len(rated),
            "dist": [sum(1 for o in rated if o["rating"] == n) for n in range(1, 6)],
        },
        branches=sorted(branches, key=lambda r: -r["orders"]),
        reviews=reviews,
        totals={
            "orders": sum(1 for o in orders if o["status"] != "cancelled"),
            "done": len(done),
            "cancelled": sum(1 for o in orders if o["status"] == "cancelled"),
            "active": sum(1 for o in orders if o["status"] in ACTIVE_STATUSES),
            "revenue": revenue,
            "avg_check": round(revenue / len(done)) if done else 0,
            "delivery": sum(1 for o in orders if o["type"] == "delivery" and o["status"] != "cancelled"),
            "pickup": sum(1 for o in orders if o["type"] == "pickup" and o["status"] != "cancelled"),
            "new_customers": await ctx.db.count_users_since(since),
            "customers_total": len(await ctx.db.all_user_ids()),
        },
        daily=[{"date": k, **v} for k, v in daily.items()],
        top=sorted(top.values(), key=lambda r: (-r["qty"], -r["revenue"]))[:10],
        busy_hours=[{"hour": h, "orders": n} for h, n in sorted(hours.items())],
    )


# =====================================================================  adminlar
@admin_route
async def list_admins(request: web.Request, ctx: AppContext) -> web.Response:
    owners = sorted(ctx.settings.admin_ids)
    users = await ctx.db.users_by_ids(owners)
    return ok(
        owners=[{"user_id": i, "name": (users.get(i) or {}).get("first_name") or ""} for i in owners],
        admins=await ctx.db.list_admins(),
        can_manage=request[IS_OWNER],
        me=request[ADMIN_ID],
    )


@admin_route
async def add_admin(request: web.Request, ctx: AppContext) -> web.Response:
    if not request[IS_OWNER]:
        raise ApiError(403, "owner_only")
    body = await _json(request)
    uid = v_int(body, "user_id", 1, 10**13)
    name = v_str(body, "name", 60)
    role = v_choice({"role": body.get("role", "admin")}, "role", ROLES)
    if ctx.is_owner(uid):
        raise _bad("user_id", "already_owner")
    await ctx.db.add_admin(uid, name, role)
    await ctx.reload_admins()
    return ok()


@admin_route
async def remove_admin(request: web.Request, ctx: AppContext) -> web.Response:
    if not request[IS_OWNER]:
        raise ApiError(403, "owner_only")
    raw = request.match_info["id"]
    if not raw.isdigit():
        raise ApiError(404, "not_found")
    await ctx.db.remove_admin(int(raw))
    await ctx.reload_admins()
    return ok()


# =====================================================================  mijozlarga xabar
@admin_route
async def broadcast_status(request: web.Request, ctx: AppContext) -> web.Response:
    return ok(state=ctx.broadcast, customers=len(await ctx.db.all_user_ids()))


@admin_route
async def broadcast_send(request: web.Request, ctx: AppContext) -> web.Response:
    body = await _json(request)
    image = v_image(body)
    text = v_str(body, "text", 1024 if image else 4096, required=not image)
    with_button = bool(body.get("menu_button"))
    if image and not MEDIA_RE.match(image):
        raise _bad("image")
    path = ctx.settings.upload_dir / image.rsplit("/", 1)[1] if image else None
    if path is not None and not path.exists():
        raise _bad("image")
    https = ctx.settings.public_url.startswith("https://")
    photo_id: dict[str, str] = {}

    async def send(uid: int, lang: str) -> None:
        markup = None
        if with_button and https:
            markup = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(
                text=t(lang, "btn_open_menu"), web_app=WebAppInfo(url=webapp_url(ctx.settings.webapp_url, lang)))]])
        if path is not None:
            msg = await ctx.bot.send_photo(uid, photo_id.get("id") or FSInputFile(path), caption=text or None,
                                           parse_mode=None, reply_markup=markup)
            if msg and msg.photo and "id" not in photo_id:
                photo_id["id"] = msg.photo[-1].file_id  # keyingilariga qayta yuklamaymiz
        else:
            await ctx.bot.send_message(uid, text, parse_mode=None, reply_markup=markup)

    if not start_broadcast(ctx, send):
        raise ApiError(409, "broadcast_running")
    return ok(state=ctx.broadcast)


# =====================================================================  marshrutlar
def setup_admin_routes(app: web.Application) -> None:
    r = app.router
    r.add_get("/admin", admin_redirect)
    r.add_get("/admin/", admin_index)
    r.add_get("/admin/login", login)
    r.add_post("/api/admin/logout", logout)
    r.add_get("/api/admin/me", me)
    r.add_post("/api/admin/upload", upload)
    r.add_get("/api/admin/menu", get_menu)
    r.add_post("/api/admin/categories", create_category)
    r.add_post("/api/admin/categories/reorder", reorder_categories)
    r.add_patch("/api/admin/categories/{id}", update_category)
    r.add_delete("/api/admin/categories/{id}", delete_category)
    r.add_post("/api/admin/products", create_product)
    r.add_post("/api/admin/products/reorder", reorder_products)
    r.add_patch("/api/admin/products/{id}", update_product)
    r.add_delete("/api/admin/products/{id}", delete_product)
    r.add_get("/api/admin/banners", get_banners)
    r.add_post("/api/admin/banners", create_banner)
    r.add_post("/api/admin/banners/reorder", reorder_banners)
    r.add_patch("/api/admin/banners/{id}", update_banner)
    r.add_delete("/api/admin/banners/{id}", delete_banner)
    r.add_get("/api/admin/branches", list_branches)
    r.add_post("/api/admin/branches", create_branch)
    r.add_post("/api/admin/branches/reorder", reorder_branches)
    r.add_patch("/api/admin/branches/{id}", update_branch)
    r.add_delete("/api/admin/branches/{id}", delete_branch)
    r.add_get("/api/admin/store", get_store)
    r.add_patch("/api/admin/store", patch_store)
    r.add_get("/api/admin/orders", list_orders)
    r.add_post("/api/admin/orders/{id}/status", set_order_status)
    r.add_get("/api/admin/stats", stats)
    r.add_get("/api/admin/admins", list_admins)
    r.add_post("/api/admin/admins", add_admin)
    r.add_delete("/api/admin/admins/{id}", remove_admin)
    r.add_get("/api/admin/broadcast", broadcast_status)
    r.add_post("/api/admin/broadcast", broadcast_send)
