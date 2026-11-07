"""Mijoz bilan muloqot: /start, til, telefon, buyurtmalarim, ma'lumot."""
from __future__ import annotations

import logging
from html import escape

from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery, MenuButtonWebApp, Message, WebAppInfo

from ..context import AppContext
from ..geo import coords_text, reverse_geocode
from ..keyboards import (
    lang_keyboard,
    location_keyboard,
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


async def _send_open_menu(message: Message, ctx: AppContext, lang: str, text: str | None = None,
                          order_type: str = "", checkout: bool = False) -> None:
    hours = ctx.catalog.store.get("hours", {})
    text = text or t(lang, "open_menu")
    if not ctx.catalog.store.get("accepting", True):
        text = t(lang, "paused_now") + "\n\n" + text
    elif not ctx.catalog.is_open():
        text = t(lang, "closed_now", open=hours.get("open", ""), close=hours.get("close", "")) + "\n\n" + text
    if _has_webapp(ctx):
        await message.answer(text, reply_markup=open_menu_keyboard(lang, ctx.settings.webapp_url, order_type, checkout))
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
    had_phone = bool((await ctx.db.get_user(u.id) or {}).get("phone"))
    await ctx.db.upsert_user(u.id, u.first_name, u.username)
    await ctx.db.set_user_field(u.id, "phone", phone)
    await message.answer(t(lang, "phone_saved"), reply_markup=_kb(ctx, lang, u.id))
    if not had_phone:  # birinchi marta (ro'yxatdan o'tish) — xush kelibsiz xabari
        await _set_menu_button(ctx, u.id, lang)
        await _send_home(message, ctx, lang, u.first_name, u.id)


# ---------- buyurtma: avval manzil (Telegram'ning o'z lokatsiya tugmasi) ----------
async def ask_location(ctx: AppContext, chat_id: int, lang: str) -> None:
    user = await ctx.db.get_user(chat_id) or {}
    s = ctx.catalog.store
    delivery = s.get("delivery", {}).get("enabled", True)
    pickup = s.get("pickup", {}).get("enabled", True)
    has_saved = user.get("last_lat") is not None
    text = t(lang, "ask_location")
    if has_saved and delivery:
        text += t(lang, "ask_location_prev", address=escape(user.get("last_address") or t(lang, "location_point")))
    if pickup:
        text += t(lang, "ask_location_pickup")
    await ctx.bot.send_message(chat_id, text, reply_markup=location_keyboard(lang, has_saved, delivery, pickup))


@router.message(F.text.in_(all_variants("btn_order")))
async def on_order(message: Message, ctx: AppContext) -> None:
    lang = await _lang(ctx, message.from_user.id)
    if not ctx.catalog.store.get("delivery", {}).get("enabled", True):
        await _send_open_menu(message, ctx, lang, order_type="pickup")
        return
    await ask_location(ctx, message.chat.id, lang)


async def _after_choice(message: Message, ctx: AppContext, lang: str, head: str, order_type: str) -> None:
    uid = message.from_user.id
    from_app = uid in ctx.location_requests
    ctx.location_requests.discard(uid)
    await message.answer(head, reply_markup=_kb(ctx, lang, uid))
    await _send_open_menu(message, ctx, lang, text=t(lang, "continue_order" if from_app else "choose_food"),
                          order_type=order_type, checkout=from_app)


@router.message(F.location)
async def on_location(message: Message, ctx: AppContext) -> None:
    u = message.from_user
    lang = await _lang(ctx, u.id)
    lat, lon = round(message.location.latitude, 6), round(message.location.longitude, 6)
    address = message.venue.address if message.venue else None
    address = address or await reverse_geocode(lat, lon, lang, ctx.settings.public_url) or coords_text(lat, lon)
    await ctx.db.upsert_user(u.id, u.first_name, u.username)
    await ctx.db.set_location(u.id, lat, lon, address)
    await _after_choice(message, ctx, lang, t(lang, "location_saved", address=escape(address)), "delivery")


@router.message(F.text.in_(all_variants("btn_prev_address")))
async def on_prev_address(message: Message, ctx: AppContext) -> None:
    lang = await _lang(ctx, message.from_user.id)
    user = await ctx.db.get_user(message.from_user.id) or {}
    if user.get("last_lat") is None:
        await ask_location(ctx, message.chat.id, lang)
        return
    await ctx.db.set_user_field(message.from_user.id, "pref_type", "delivery")
    address = user.get("last_address") or coords_text(user["last_lat"], user["last_lon"])
    await _after_choice(message, ctx, lang, t(lang, "location_saved", address=escape(address)), "delivery")


@router.message(F.text.in_(all_variants("btn_pickup_self")))
async def on_pickup(message: Message, ctx: AppContext) -> None:
    lang = await _lang(ctx, message.from_user.id)
    await ctx.db.set_user_field(message.from_user.id, "pref_type", "pickup")
    address = ctx.catalog.store.get("address", {}).get(lang, "")
    await _after_choice(message, ctx, lang, t(lang, "pickup_chosen", address=escape(address)), "pickup")


@router.message(F.text.in_(all_variants("btn_back")))
async def on_back(message: Message, ctx: AppContext) -> None:
    lang = await _lang(ctx, message.from_user.id)
    ctx.location_requests.discard(message.from_user.id)
    await message.answer(t(lang, "home_menu"), reply_markup=_kb(ctx, lang, message.from_user.id))


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
