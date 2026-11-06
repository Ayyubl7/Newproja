"""Admin: buyurtma holatlari, stop-list, statistika, reklama yuborish."""
from __future__ import annotations

import asyncio
import logging
from html import escape
from typing import Any

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError, TelegramRetryAfter
from aiogram.filters import BaseFilter, Command
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

from ..catalog import Catalog, fmt_money
from ..config import DATA_DIR
from ..context import AppContext, spawn
from ..db import days_ago_utc, start_of_today_utc
from ..orders import (
    OrderCb,
    admin_keyboard,
    admin_text,
    can_transition,
    cancel_confirm_keyboard,
    item_lines,
    notify_user_status,
)
from ..texts import at, t

log = logging.getLogger(__name__)
router = Router(name="admin")


class IsAdmin(BaseFilter):
    async def __call__(self, event: Message | CallbackQuery, ctx: AppContext) -> bool:
        chat = event.chat if isinstance(event, Message) else (event.message.chat if event.message else None)
        return ctx.is_admin(event.from_user.id if event.from_user else None, chat.id if chat else None)


# ---------- /id: sozlash uchun (hamma uchun ochiq) ----------
@router.message(Command("id"))
async def cmd_id(message: Message, ctx: AppContext) -> None:
    await message.answer(at(ctx.settings.admin_lang, "chat_id", chat_id=message.chat.id,
                            user_id=message.from_user.id if message.from_user else 0))


# ---------- buyurtma holati ----------
@router.callback_query(OrderCb.filter())
async def cb_order(call: CallbackQuery, callback_data: OrderCb, ctx: AppContext) -> None:
    lang = ctx.settings.admin_lang
    if not ctx.is_admin(call.from_user.id, call.message.chat.id if call.message else None):
        await call.answer(at(lang, "not_admin"), show_alert=True)
        return

    if not isinstance(call.message, Message):
        await call.answer(at(lang, "status_stale"), show_alert=True)  # 48 soatdan eski xabar
        return
    order = await ctx.db.get_order(callback_data.id)
    if order is None:
        await call.answer("?", show_alert=True)
        return
    action = callback_data.action

    if action == "ask_cancel":
        if order["status"] in ("new", "accepted"):
            await call.message.edit_reply_markup(reply_markup=cancel_confirm_keyboard(ctx, order["id"]))
            await call.answer(at(lang, "confirm_cancel", id=order["id"]))
        else:
            await call.answer(at(lang, "status_stale"), show_alert=True)
        return
    if action == "back":
        await call.message.edit_reply_markup(reply_markup=admin_keyboard(ctx, order))
        await call.answer()
        return

    if not can_transition(order, action) or not await ctx.db.update_status(order["id"], order["status"], action):
        await call.answer(at(lang, "status_stale"), show_alert=True)
        order = await ctx.db.get_order(order["id"])
        await _refresh(call, ctx, order, None)
        return

    order = await ctx.db.get_order(order["id"])
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


@admin_cmds.message(Command("stats"))
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


@admin_cmds.message(Command("reload"))
async def cmd_reload(message: Message, ctx: AppContext) -> None:
    lang = ctx.settings.admin_lang
    try:
        fresh = Catalog.load(DATA_DIR)
    except Exception as e:  # noqa: BLE001 — xatoni adminga ko'rsatamiz
        await message.answer(at(lang, "reload_error", error=escape(str(e))))
        return
    fresh.stoplist = await ctx.db.stoplist()
    ctx.catalog = fresh
    await message.answer(at(lang, "reloaded", cats=len(fresh.categories), products=len(fresh.products)))


# ---------- stop-list ----------
def _stop_home_kb(ctx: AppContext) -> InlineKeyboardMarkup:
    lang = ctx.settings.admin_lang
    rows, row = [], []
    for c in ctx.catalog.categories:
        stopped = sum(1 for p in ctx.catalog.products.values()
                      if p["category"] == c["id"] and p["id"] in ctx.catalog.stoplist)
        label = c["name"].get(lang, c["id"]) + (f" (⛔{stopped})" if stopped else "")
        row.append(InlineKeyboardButton(text=label, callback_data=f"sl:c:{c['id']}"))
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
        mark = "⛔" if p["id"] in ctx.catalog.stoplist else "✅"
        rows.append([InlineKeyboardButton(text=f"{mark} {p['name'].get(lang, p['id'])}",
                                          callback_data=f"sl:t:{p['id']}")])
    rows.append([InlineKeyboardButton(text=at(lang, "btn_back"), callback_data="sl:home")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def _cat_name(ctx: AppContext, cat_id: str) -> str:
    for c in ctx.catalog.categories:
        if c["id"] == cat_id:
            return c["name"].get(ctx.settings.admin_lang, cat_id)
    return cat_id


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
    elif kind == "c":
        await call.message.edit_text(at(lang, "stoplist_cat", cat=escape(_cat_name(ctx, value))),
                                     reply_markup=_stop_cat_kb(ctx, value))
    elif kind == "t" and value in ctx.catalog.products:
        stopped = await ctx.db.toggle_stop(value)
        if stopped:
            ctx.catalog.stoplist.add(value)
        else:
            ctx.catalog.stoplist.discard(value)
        cat_id = ctx.catalog.products[value]["category"]
        await call.message.edit_reply_markup(reply_markup=_stop_cat_kb(ctx, cat_id))
    await call.answer()


# ---------- reklama ----------
@admin_cmds.message(Command("broadcast"))
async def cmd_broadcast(message: Message, ctx: AppContext) -> None:
    lang = ctx.settings.admin_lang
    src = message.reply_to_message
    if src is None:
        await message.answer(at(lang, "broadcast_help"))
        return
    user_ids = await ctx.db.all_user_ids()
    await message.answer(at(lang, "broadcast_start", count=len(user_ids)))
    spawn(_broadcast(ctx, message, src, user_ids))


async def _broadcast(ctx: AppContext, report_to: Message, src: Message, user_ids: list[int]) -> None:
    ok = fail = 0
    for uid in user_ids:
        for _ in range(3):
            try:
                await ctx.bot.copy_message(uid, src.chat.id, src.message_id)
                ok += 1
                break
            except TelegramRetryAfter as e:
                await asyncio.sleep(e.retry_after + 0.5)
            except (TelegramForbiddenError, TelegramBadRequest):
                fail += 1
                break
            except Exception:
                log.exception("Broadcast xatosi")
                fail += 1
                break
        await asyncio.sleep(0.05)  # Telegram limiti: ~30 xabar/soniya
    await report_to.answer(at(ctx.settings.admin_lang, "broadcast_done", ok=ok, fail=fail))
