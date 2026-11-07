"""Admin: panelni ochish, buyurtma holatlari, stop-list, statistika, reklama yuborish."""
from __future__ import annotations

import logging
from html import escape
from typing import Any

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import BaseFilter, Command, CommandStart
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message, WebAppInfo

from ..broadcast import start_broadcast
from ..catalog import fmt_money
from ..context import AppContext
from ..db import days_ago_utc, start_of_today_utc
from ..orders import (
    OrderCb,
    admin_keyboard,
    admin_text,
    apply_status,
    cancel_confirm_keyboard,
    item_lines,
    notify_user_status,
)
from ..texts import ADMIN_PANEL_BUTTON, at, t

log = logging.getLogger(__name__)
router = Router(name="admin")


class IsAdmin(BaseFilter):
    """Panel adminlari yoki admin guruhi ichidagi har kim."""

    async def __call__(self, event: Message | CallbackQuery, ctx: AppContext) -> bool:
        chat = event.chat if isinstance(event, Message) else (event.message.chat if event.message else None)
        return ctx.is_admin(event.from_user.id if event.from_user else None, chat.id if chat else None)


class IsFullAdmin(BaseFilter):
    """Ega yoki administrator (kassirga yopiq amallar uchun)."""

    async def __call__(self, event: Message | CallbackQuery, ctx: AppContext) -> bool:
        return bool(event.from_user) and ctx.is_full_admin(event.from_user.id)


class StatsAccess(BaseFilter):
    """Statistika: admin guruhida hamma xodim, shaxsiy chatda — faqat ega/administrator."""

    async def __call__(self, message: Message, ctx: AppContext) -> bool:
        uid = message.from_user.id if message.from_user else None
        return message.chat.id == ctx.settings.admin_chat_id or ctx.is_full_admin(uid)


class IsPanelAdmin(BaseFilter):
    async def __call__(self, event: Message, ctx: AppContext) -> bool:
        return bool(event.from_user) and ctx.is_panel_admin(event.from_user.id)


# ---------- /id: sozlash uchun (hamma uchun ochiq) ----------
@router.message(Command("id"))
async def cmd_id(message: Message, ctx: AppContext) -> None:
    await message.answer(at(ctx.settings.admin_lang, "chat_id", chat_id=message.chat.id,
                            user_id=message.from_user.id if message.from_user else 0))


# ---------- admin panel ----------
async def send_panel(message: Message, ctx: AppContext, user_id: int) -> None:
    lang = ctx.settings.admin_lang
    url = ctx.settings.public_url
    if not url.startswith("https://"):
        await message.answer(at(lang, "panel_no_https"))
        return
    token = ctx.new_login_token(user_id)
    await message.answer(at(lang, "panel_text"), reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=at(lang, "panel_open"), web_app=WebAppInfo(url=f"{url}/admin/"))],
        [InlineKeyboardButton(text=at(lang, "panel_desktop"), url=f"{url}/admin/login?t={token}")],
    ]))


@router.message(CommandStart(deep_link=True, magic=F.args == "panel"), F.chat.type == "private", IsPanelAdmin())
async def start_panel(message: Message, ctx: AppContext) -> None:
    await send_panel(message, ctx, message.from_user.id)


@router.message(Command("panel"))
@router.message(F.text == ADMIN_PANEL_BUTTON)
async def cmd_panel(message: Message, ctx: AppContext) -> None:
    lang = ctx.settings.admin_lang
    uid = message.from_user.id if message.from_user else 0
    if message.chat.type != "private":
        if not ctx.is_admin(uid, message.chat.id):
            return
        me = await ctx.bot.me()
        await message.answer(at(lang, "panel_private_only"), reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text=at(lang, "panel_open"), url=f"https://t.me/{me.username}?start=panel")]]))
        return
    if not ctx.is_panel_admin(uid):
        await message.answer(at(lang, "panel_no_access", user_id=uid))
        return
    await send_panel(message, ctx, uid)


# ---------- buyurtma holati (guruhdagi tugmalar) ----------
@router.callback_query(OrderCb.filter())
async def cb_order(call: CallbackQuery, callback_data: OrderCb, ctx: AppContext) -> None:
    lang = ctx.settings.admin_lang
    if not ctx.is_admin(call.from_user.id, call.message.chat.id if call.message else None):
        await call.answer(at(lang, "not_admin"), show_alert=True)
        return
    if not isinstance(call.message, Message):
        await call.answer(at(lang, "status_stale"), show_alert=True)  # 48 soatdan eski xabar
        return

    action = callback_data.action
    if action in ("ask_cancel", "back"):
        order = await ctx.db.get_order(callback_data.id)
        if order is None:
            await call.answer("?", show_alert=True)
            return
        if action == "back":
            await call.message.edit_reply_markup(reply_markup=admin_keyboard(ctx, order))
            await call.answer()
        elif order["status"] in ("new", "accepted"):
            await call.message.edit_reply_markup(reply_markup=cancel_confirm_keyboard(ctx, order["id"]))
            await call.answer(at(lang, "confirm_cancel", id=order["id"]))
        else:
            await call.answer(at(lang, "status_stale"), show_alert=True)
        return

    success, order = await apply_status(ctx, callback_data.id, action)
    if order is None:
        await call.answer("?", show_alert=True)
        return
    if not success:
        await call.answer(at(lang, "status_stale"), show_alert=True)
        await _refresh(call, ctx, order, None)
        return
    await _refresh(call, ctx, order, call.from_user.full_name)
    await call.answer(at(lang, "status_changed", status=t(lang, "st_" + order["status"])))
    await notify_user_status(ctx, order)


async def _refresh(call: CallbackQuery, ctx: AppContext, order: dict[str, Any], by: str | None) -> None:
    user = await ctx.db.get_user(order["user_id"])
    try:
        await call.message.edit_text(admin_text(ctx, order, user, changed_by=by),
                                     reply_markup=admin_keyboard(ctx, order), disable_web_page_preview=True)
    except TelegramBadRequest:
        pass  # matn o'zgarmagan


# ---------- admin buyruqlari ----------
admin_cmds = Router(name="admin_cmds")
admin_cmds.message.filter(IsAdmin())
admin_cmds.callback_query.filter(IsAdmin())
router.include_router(admin_cmds)


@admin_cmds.message(Command("admin", "help"))
async def cmd_help(message: Message, ctx: AppContext) -> None:
    await message.answer(at(ctx.settings.admin_lang, "admin_help"))


@admin_cmds.message(Command("active"))
async def cmd_active(message: Message, ctx: AppContext) -> None:
    lang = ctx.settings.admin_lang
    orders = await ctx.db.active_orders()
    if not orders:
        await message.answer(at(lang, "active_none"))
        return
    blocks = [at(lang, "active_title")]
    for o in orders[:30]:
        blocks.append(
            f"<b>#{o['id']}</b> · {t(lang, 'st_' + o['status'])} · {t(lang, 'type_' + o['type'])}\n"
            f"📞 {escape(o['phone'])} · {fmt_money(o['total'], lang)}\n{item_lines(o['items'], lang)}"
        )
    await message.answer("\n\n".join(blocks))


@admin_cmds.message(Command("stats"), StatsAccess())
async def cmd_stats(message: Message, ctx: AppContext) -> None:
    lang = ctx.settings.admin_lang
    today = await ctx.db.stats_since(start_of_today_utc())
    week = await ctx.db.stats_since(days_ago_utc(6))
    active = len(await ctx.db.active_orders())
    users = len(await ctx.db.all_user_ids())
    await message.answer(at(
        lang, "stats",
        t_total=today["total"], t_done=today["done"], t_cancelled=today["cancelled"],
        t_revenue=fmt_money(today["revenue"], lang),
        w_total=week["total"], w_done=week["done"], w_revenue=fmt_money(week["revenue"], lang),
        active=active, users=users,
    ))


# ---------- stop-list ----------
def _stop_home_kb(ctx: AppContext) -> InlineKeyboardMarkup:
    lang = ctx.settings.admin_lang
    rows, row = [], []
    for c in ctx.catalog.categories:
        stopped = sum(1 for p in ctx.catalog.products.values() if p["category"] == c["id"] and not p["available"])
        label = c["name"].get(lang) or c["id"]
        row.append(InlineKeyboardButton(text=label + (f" (⛔{stopped})" if stopped else ""),
                                        callback_data=f"sl:c:{c['id']}"))
        if len(row) == 2:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    return InlineKeyboardMarkup(inline_keyboard=rows)


def _stop_cat_kb(ctx: AppContext, cat_id: str) -> InlineKeyboardMarkup:
    lang = ctx.settings.admin_lang
    rows = []
    for p in ctx.catalog.products.values():
        if p["category"] != cat_id:
            continue
        mark = "✅" if p["available"] else "⛔"
        rows.append([InlineKeyboardButton(text=f"{mark} {p['name'].get(lang) or p['id']}",
                                          callback_data=f"sl:t:{p['id']}")])
    rows.append([InlineKeyboardButton(text=at(lang, "btn_back"), callback_data="sl:home")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


@admin_cmds.message(Command("stoplist", "stop"))
async def cmd_stoplist(message: Message, ctx: AppContext) -> None:
    await message.answer(at(ctx.settings.admin_lang, "stoplist_title"), reply_markup=_stop_home_kb(ctx))


@admin_cmds.callback_query(F.data.startswith("sl:"))
async def cb_stoplist(call: CallbackQuery, ctx: AppContext) -> None:
    lang = ctx.settings.admin_lang
    _, kind, *rest = call.data.split(":", 2)
    value = rest[0] if rest else ""
    if kind == "home":
        await call.message.edit_text(at(lang, "stoplist_title"), reply_markup=_stop_home_kb(ctx))
    elif kind == "c" and ctx.catalog.category(value):
        name = ctx.catalog.category(value)["name"].get(lang) or value
        await call.message.edit_text(at(lang, "stoplist_cat", cat=escape(name)), reply_markup=_stop_cat_kb(ctx, value))
    elif kind == "t" and value in ctx.catalog.products:
        product = ctx.catalog.products[value]
        await ctx.db.update_product(value, {"available": not product["available"]})
        await ctx.reload_catalog()
        await call.message.edit_reply_markup(reply_markup=_stop_cat_kb(ctx, product["category"]))
    await call.answer()


# ---------- reklama (xabarga reply qilib) ----------
@admin_cmds.message(Command("broadcast"), IsFullAdmin())
async def cmd_broadcast(message: Message, ctx: AppContext) -> None:
    lang = ctx.settings.admin_lang
    src = message.reply_to_message
    if src is None:
        await message.answer(at(lang, "broadcast_help"))
        return

    async def send(uid: int, _lang: str) -> None:
        await ctx.bot.copy_message(uid, src.chat.id, src.message_id)

    async def report(st: dict[str, Any]) -> None:
        await message.answer(at(lang, "broadcast_done", ok=st["ok"], fail=st["fail"]))

    if not start_broadcast(ctx, send, report):
        await message.answer(at(lang, "broadcast_running"))
        return
    await message.answer(at(lang, "broadcast_start", count=len(await ctx.db.all_user_ids())))
