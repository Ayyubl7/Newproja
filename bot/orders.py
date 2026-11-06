"""Buyurtma xabarlari: adminga yuborish, holatlar, mijozga bildirishnoma."""
from __future__ import annotations

import asyncio
import logging
from datetime import datetime
from html import escape
from typing import Any

from aiogram.exceptions import TelegramAPIError, TelegramForbiddenError, TelegramRetryAfter
from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from .catalog import TASHKENT_TZ, fmt_money
from .context import AppContext
from .db import local_time
from .texts import at, norm_lang, t

log = logging.getLogger(__name__)

# Qaysi holatdan qaysiga o'tish mumkin
TRANSITIONS: dict[str, tuple[str, ...]] = {
    "new": ("accepted", "cancelled"),
    "accepted": ("on_the_way", "ready", "cancelled"),
    "on_the_way": ("done",),
    "ready": ("done",),
}
ACTIVE_STATUSES = tuple(TRANSITIONS)


class OrderCb(CallbackData, prefix="o"):
    id: int
    action: str  # accepted | on_the_way | ready | done | cancelled | ask_cancel | back


def can_transition(order: dict[str, Any], new_status: str) -> bool:
    if new_status not in TRANSITIONS.get(order["status"], ()):
        return False
    if new_status == "on_the_way" and order["type"] != "delivery":
        return False
    if new_status == "ready" and order["type"] != "pickup":
        return False
    return True


# ---------- matn yasash ----------
def item_lines(items: list[dict[str, Any]], lang: str) -> str:
    lang = norm_lang(lang)
    rows = []
    for it in items:
        name = escape(it["name"].get(lang) or it["name"].get("uz") or it["id"])
        rows.append(f"• {name} × {it['qty']} = {fmt_money(it['price'] * it['qty'], lang)}")
    return "\n".join(rows)


def summary_lines(order: dict[str, Any], lang: str) -> str:
    rows = [t(lang, "sum_items", v=fmt_money(order["subtotal"], lang))]
    if order["type"] == "delivery":
        fee = order["delivery_fee"]
        rows.append(t(lang, "sum_delivery", v=fmt_money(fee, lang) if fee else t(lang, "sum_free")))
    rows.append(t(lang, "sum_total", v=fmt_money(order["total"], lang)))
    return "\n".join(rows)


def map_links(lat: float, lon: float) -> str:
    return (
        f'<a href="https://yandex.uz/maps/?pt={lon},{lat}&z=17&l=map">Yandex</a> · '
        f'<a href="https://maps.google.com/?q={lat},{lon}">Google</a>'
    )


def admin_text(ctx: AppContext, order: dict[str, Any], user: dict[str, Any] | None = None,
               changed_by: str | None = None) -> str:
    lang = ctx.settings.admin_lang
    name = escape(order.get("name") or "—")
    if user and user.get("username"):
        name += f" (@{escape(user['username'])})"
    name += f' · <a href="tg://user?id={order["user_id"]}">profil</a>'

    parts = [
        at(lang, "new_order" if order["status"] == "new" else "order_title", id=order["id"]),
        "━━━━━━━━━━━━",
        at(lang, "customer", name=name),
        at(lang, "phone", phone=escape(order["phone"])),
        at(lang, "type", type=t(lang, f"type_{order['type']}")),
    ]
    if order["type"] == "delivery":
        parts.append(at(lang, "address", address=escape(order.get("address") or "—")))
        if order.get("lat") is not None and order.get("lon") is not None:
            parts.append(at(lang, "map", links=map_links(order["lat"], order["lon"])))
    if order.get("comment"):
        parts.append(at(lang, "comment", comment=escape(order["comment"])))
    parts.append(at(lang, "payment", payment=t(lang, f"pay_{order['payment']}")))
    parts += ["", item_lines(order["items"], lang), "━━━━━━━━━━━━", summary_lines(order, lang)]

    created = local_time(order["created_at"]).strftime("%H:%M, %d.%m.%Y")
    parts.append(f"🕒 {created}")
    status = at(lang, "status", status=t(lang, f"st_{order['status']}"))
    if changed_by:
        status += " " + at(lang, "changed_by", by=escape(changed_by),
                           time=datetime.now(TASHKENT_TZ).strftime("%H:%M"))
    parts.append(status)
    return "\n".join(parts)


def admin_keyboard(ctx: AppContext, order: dict[str, Any]) -> InlineKeyboardMarkup | None:
    lang = ctx.settings.admin_lang
    oid, status = order["id"], order["status"]

    def btn(key: str, action: str) -> InlineKeyboardButton:
        return InlineKeyboardButton(text=at(lang, key), callback_data=OrderCb(id=oid, action=action).pack())

    if status == "new":
        rows = [[btn("btn_accept", "accepted"), btn("btn_cancel", "ask_cancel")]]
    elif status == "accepted":
        nxt = btn("btn_on_the_way", "on_the_way") if order["type"] == "delivery" else btn("btn_ready", "ready")
        rows = [[nxt], [btn("btn_cancel", "ask_cancel")]]
    elif status in ("on_the_way", "ready"):
        rows = [[btn("btn_done", "done")]]
    else:
        return None
    return InlineKeyboardMarkup(inline_keyboard=rows)


def cancel_confirm_keyboard(ctx: AppContext, order_id: int) -> InlineKeyboardMarkup:
    lang = ctx.settings.admin_lang
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text=at(lang, "btn_confirm_cancel"),
                             callback_data=OrderCb(id=order_id, action="cancelled").pack()),
        InlineKeyboardButton(text=at(lang, "btn_back"),
                             callback_data=OrderCb(id=order_id, action="back").pack()),
    ]])


def user_order_created_text(ctx: AppContext, order: dict[str, Any]) -> str:
    lang = order["lang"]
    store = ctx.catalog.store
    if order["type"] == "delivery":
        where = t(lang, "where_delivery", address=escape(order.get("address") or ""))
    else:
        where = t(lang, "where_pickup", address=escape(store.get("address", {}).get(lang, "")))
    return t(
        lang, "order_created", id=order["id"], items=item_lines(order["items"], lang),
        summary=summary_lines(order, lang), payment=t(lang, f"pay_{order['payment']}"), where=where,
    )


def user_status_text(ctx: AppContext, order: dict[str, Any]) -> str | None:
    lang = order["lang"]
    store = ctx.catalog.store
    key = f"notify_{order['status']}"
    if order["status"] == "new":
        return None
    return t(lang, key, id=order["id"], phone=escape(store.get("phone", "")),
             address=escape(store.get("address", {}).get(lang, "")))


def user_order_short(order: dict[str, Any], lang: str) -> str:
    created = local_time(order["created_at"]).strftime("%d.%m %H:%M")
    return (
        f"<b>#{order['id']}</b> · {created} · {t(lang, 'st_' + order['status'])}\n"
        f"{item_lines(order['items'], lang)}\n"
        f"{t(lang, 'sum_total', v=fmt_money(order['total'], lang))}"
    )


# ---------- yuborish ----------
async def _with_retry(coro_factory, attempts: int = 4):
    """Telegram «juda ko'p so'rov» desa, kutib qayta urinadi (guruhda limit: ~20 xabar/daqiqa)."""
    for i in range(attempts):
        try:
            return await coro_factory()
        except TelegramRetryAfter as e:
            log.warning("Telegram limit, %ss kutamiz", e.retry_after)
            await asyncio.sleep(e.retry_after + 0.5)
        except TelegramForbiddenError:
            raise
        except TelegramAPIError:
            if i == attempts - 1:
                raise
            await asyncio.sleep(1.5 * (i + 1))
    return None


async def announce_new_order(ctx: AppContext, order_id: int) -> None:
    """Yangi buyurtmani admin guruhiga va mijozga yuboradi. Fon vazifasi sifatida ishlaydi."""
    order = await ctx.db.get_order(order_id)
    if order is None:
        return
    user = await ctx.db.get_user(order["user_id"])

    if ctx.settings.admin_chat_id:
        try:
            msg = await _with_retry(lambda: ctx.bot.send_message(
                ctx.settings.admin_chat_id, admin_text(ctx, order, user),
                reply_markup=admin_keyboard(ctx, order), disable_web_page_preview=True,
            ))
            if msg is not None:
                await ctx.db.set_admin_message(order_id, msg.message_id)
        except Exception:
            log.exception("Buyurtma #%s admin guruhiga yuborilmadi", order_id)
    else:
        log.warning("ADMIN_CHAT_ID sozlanmagan — buyurtma #%s faqat bazada", order_id)

    try:
        await _with_retry(lambda: ctx.bot.send_message(order["user_id"], user_order_created_text(ctx, order)))
    except Exception:
        log.info("Mijozga #%s tasdig'i yuborilmadi (user_id=%s)", order_id, order["user_id"])


async def notify_user_status(ctx: AppContext, order: dict[str, Any]) -> None:
    text = user_status_text(ctx, order)
    if not text:
        return
    try:
        await _with_retry(lambda: ctx.bot.send_message(order["user_id"], text))
    except Exception:
        log.info("Mijozga #%s holati yuborilmadi", order["id"])


async def apply_status(ctx: AppContext, order_id: int, new_status: str) -> tuple[bool, dict[str, Any] | None]:
    """Holatni bazada o'zgartiradi. (muvaffaqiyat, buyurtmaning hozirgi holati)."""
    order = await ctx.db.get_order(order_id)
    if order is None:
        return False, None
    if not can_transition(order, new_status) or not await ctx.db.update_status(order_id, order["status"], new_status):
        return False, await ctx.db.get_order(order_id)
    return True, await ctx.db.get_order(order_id)


async def sync_admin_message(ctx: AppContext, order: dict[str, Any], changed_by: str | None) -> None:
    """Admin paneldan o'zgartirilganda guruhdagi buyurtma xabarini ham yangilaydi."""
    if not ctx.settings.admin_chat_id or not order.get("admin_message_id"):
        return
    user = await ctx.db.get_user(order["user_id"])
    try:
        await ctx.bot.edit_message_text(
            text=admin_text(ctx, order, user, changed_by=changed_by),
            chat_id=ctx.settings.admin_chat_id, message_id=order["admin_message_id"],
            reply_markup=admin_keyboard(ctx, order), disable_web_page_preview=True,
        )
    except Exception:
        log.info("Guruhdagi #%s xabarini yangilab bo'lmadi", order["id"])
