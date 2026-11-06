"""Mijoz bilan muloqot: /start, til, telefon, buyurtmalarim, ma'lumot."""
from __future__ import annotations

import logging
from html import escape

from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery, MenuButtonWebApp, Message, WebAppInfo

from ..context import AppContext
from ..keyboards import (
    lang_keyboard,
    main_keyboard,
    open_menu_keyboard,
    phone_keyboard,
    settings_keyboard,
    webapp_url,
)
from ..orders import user_order_short
from ..texts import all_variants, norm_lang, t

log = logging.getLogger(__name__)
router = Router(name="user")
# Admin guruhida mijoz menyusi ishlamasin
router.message.filter(F.chat.type == "private")
router.callback_query.filter(F.message.chat.type == "private")


def _has_webapp(ctx: AppContext) -> bool:
    return ctx.settings.public_url.startswith("https://")


async def _set_menu_button(ctx: AppContext, chat_id: int, lang: str) -> None:
    if not _has_webapp(ctx):
        return
    try:
        await ctx.bot.set_chat_menu_button(
            chat_id=chat_id,
            menu_button=MenuButtonWebApp(
                text=t(lang, "menu_button"),
                web_app=WebAppInfo(url=webapp_url(ctx.settings.webapp_url, lang)),
            ),
        )
    except Exception:
        log.exception("Menyu tugmasini o'rnatib bo'lmadi")


def _kb(ctx: AppContext, lang: str, user_id: int):
    return main_keyboard(lang, admin=ctx.is_panel_admin(user_id))


async def _send_home(message: Message, ctx: AppContext, lang: str, name: str, user_id: int) -> None:
    store = ctx.catalog.store
    await message.answer(
        t(lang, "welcome", name=escape(name or ""), store=escape(store.get("name", "")),
          tagline=escape(store.get("tagline", {}).get(lang, ""))),
        reply_markup=_kb(ctx, lang, user_id),
    )
    await _send_open_menu(message, ctx, lang)


async def _send_open_menu(message: Message, ctx: AppContext, lang: str) -> None:
    hours = ctx.catalog.store.get("hours", {})
    text = t(lang, "open_menu")
    if not ctx.catalog.store.get("accepting", True):
        text = t(lang, "paused_now") + "\n\n" + text
    elif not ctx.catalog.is_open():
        text = t(lang, "closed_now", open=hours.get("open", ""), close=hours.get("close", "")) + "\n\n" + text
    if _has_webapp(ctx):
        await message.answer(text, reply_markup=open_menu_keyboard(lang, ctx.settings.webapp_url))
    else:
        await message.answer(text + "\n\n⚠️ PUBLIC_URL (https) sozlanmagan — Mini App ochilmaydi.")


async def _lang(ctx: AppContext, user_id: int) -> str:
    user = await ctx.db.get_user(user_id)
    return norm_lang(user.get("lang") if user else None)


@router.message(CommandStart())
async def cmd_start(message: Message, ctx: AppContext) -> None:
    u = message.from_user
    await ctx.db.upsert_user(u.id, u.first_name, u.username)
    user = await ctx.db.get_user(u.id)
    if not user.get("lang"):
        await message.answer(t("uz", "choose_lang"), reply_markup=lang_keyboard())
        return
    lang = norm_lang(user["lang"])
    if not user.get("phone"):
        await message.answer(t(lang, "ask_phone"), reply_markup=phone_keyboard(lang))
        return
    await _set_menu_button(ctx, u.id, lang)
    await _send_home(message, ctx, lang, u.first_name, u.id)


@router.callback_query(F.data.startswith("lang:"))
async def cb_lang(call: CallbackQuery, ctx: AppContext) -> None:
    lang = norm_lang(call.data.split(":", 1)[1])
    u = call.from_user
    await ctx.db.upsert_user(u.id, u.first_name, u.username)
    await ctx.db.set_user_field(u.id, "lang", lang)
    await _set_menu_button(ctx, u.id, lang)
    await call.answer(t(lang, "lang_saved"))
    try:
        await call.message.edit_text(t(lang, "lang_saved"))
    except Exception:
        pass
    user = await ctx.db.get_user(u.id)
    if not user.get("phone"):
        await call.message.answer(t(lang, "ask_phone"), reply_markup=phone_keyboard(lang))
    else:
        await _send_home(call.message, ctx, lang, u.first_name, u.id)


@router.message(F.contact)
async def on_contact(message: Message, ctx: AppContext) -> None:
    lang = await _lang(ctx, message.from_user.id)
    contact = message.contact
    if contact.user_id and contact.user_id != message.from_user.id:
        await message.answer(t(lang, "phone_not_own"), reply_markup=phone_keyboard(lang))
        return
    phone = contact.phone_number
    if not phone.startswith("+"):
        phone = "+" + phone
    u = message.from_user
    await ctx.db.upsert_user(u.id, u.first_name, u.username)
    await ctx.db.set_user_field(u.id, "phone", phone)
    await message.answer(t(lang, "phone_saved"), reply_markup=_kb(ctx, lang, u.id))
    await _set_menu_button(ctx, u.id, lang)
    await _send_home(message, ctx, lang, u.first_name, u.id)


@router.message(F.text.in_(all_variants("btn_order")))
async def on_order(message: Message, ctx: AppContext) -> None:
    lang = await _lang(ctx, message.from_user.id)
    await _send_open_menu(message, ctx, lang)


@router.message(F.text.in_(all_variants("btn_my_orders")))
async def on_my_orders(message: Message, ctx: AppContext) -> None:
    lang = await _lang(ctx, message.from_user.id)
    orders = await ctx.db.user_orders(message.from_user.id, limit=5)
    if not orders:
        await message.answer(t(lang, "no_orders"))
        await _send_open_menu(message, ctx, lang)
        return
    blocks = [t(lang, "my_orders_title")] + [user_order_short(o, lang) for o in orders]
    await message.answer("\n\n".join(blocks))


@router.message(F.text.in_(all_variants("btn_about")))
async def on_about(message: Message, ctx: AppContext) -> None:
    lang = await _lang(ctx, message.from_user.id)
    s = ctx.catalog.store
    hours = s.get("hours", {})
    await message.answer(t(
        lang, "about", store=escape(s.get("name", "")), about=escape(s.get("about", {}).get(lang, "")),
        open=hours.get("open", ""), close=hours.get("close", ""),
        address=escape(s.get("address", {}).get(lang, "")),
    ))
    loc = s.get("location")
    if isinstance(loc, dict) and loc.get("lat") and loc.get("lon"):
        await message.answer_location(latitude=loc["lat"], longitude=loc["lon"])


@router.message(F.text.in_(all_variants("btn_contacts")))
async def on_contacts(message: Message, ctx: AppContext) -> None:
    lang = await _lang(ctx, message.from_user.id)
    s = ctx.catalog.store
    text = t(lang, "contacts", phone=escape(s.get("phone", "")))
    if s.get("support_username"):
        text += t(lang, "contacts_tg", username=escape(s["support_username"].lstrip("@")))
    if s.get("instagram"):
        text += t(lang, "contacts_ig", instagram=escape(s["instagram"].lstrip("@")))
    await message.answer(text, disable_web_page_preview=True)


@router.message(F.text.in_(all_variants("btn_settings")))
async def on_settings(message: Message, ctx: AppContext) -> None:
    user = await ctx.db.get_user(message.from_user.id) or {}
    lang = norm_lang(user.get("lang"))
    await message.answer(
        t(lang, "settings", phone=escape(user.get("phone") or t(lang, "not_set"))),
        reply_markup=settings_keyboard(lang),
    )


@router.callback_query(F.data == "settings:lang")
async def cb_settings_lang(call: CallbackQuery) -> None:
    await call.answer()
    await call.message.answer(t("uz", "choose_lang"), reply_markup=lang_keyboard())


@router.callback_query(F.data == "settings:phone")
async def cb_settings_phone(call: CallbackQuery, ctx: AppContext) -> None:
    lang = await _lang(ctx, call.from_user.id)
    await call.answer()
    await call.message.answer(t(lang, "ask_phone"), reply_markup=phone_keyboard(lang))


@router.message()
async def fallback(message: Message, ctx: AppContext) -> None:
    lang = await _lang(ctx, message.from_user.id)
    await message.answer(t(lang, "unknown"), reply_markup=_kb(ctx, lang, message.from_user.id))
