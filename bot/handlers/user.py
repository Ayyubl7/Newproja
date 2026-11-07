"""Mijoz bilan muloqot.

Ro'yxatdan o'tish: til → telefon → ism → manzil (yoki olib ketish filiali) → menyu.
Qaysi qadam qolgani bazadagi profildan aniqlanadi — bot qayta ishga tushsa ham oqim buzilmaydi.
FSM holatlari faqat sozlamalardan o'zgartirish va bahodan keyingi izoh uchun.
"""
from __future__ import annotations

import logging
import re
from html import escape
from typing import Any

from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, MenuButtonWebApp, Message, WebAppInfo

from ..context import AppContext
from ..geo import coords_text, reverse_geocode
from ..keyboards import (
    branches_keyboard,
    cancel_confirm_keyboard,
    lang_keyboard,
    location_keyboard,
    main_keyboard,
    my_orders_keyboard,
    name_keyboard,
    order_panel_keyboard,
    phone_keyboard,
    settings_keyboard,
    skip_keyboard,
    webapp_url,
)
from ..orders import customer_cancelled, customer_rated, notify_staff, stars, user_order_short
from ..texts import all_variants, at, norm_lang, t

log = logging.getLogger(__name__)
router = Router(name="user")
# Admin guruhida mijoz menyusi ishlamasin
router.message.filter(F.chat.type == "private")
router.callback_query.filter(F.message.chat.type == "private")

PHONE_RE = re.compile(r"^\+?[0-9][0-9 ()\-]{6,20}$")
ADDRESS_MIN, ADDRESS_MAX = 5, 200


class Edit(StatesGroup):
    """Sozlamalardan o'zgartirish va past bahodan keyingi izoh."""
    phone = State()
    name = State()
    address = State()
    feedback = State()


# =====================================================================  yordamchilar
def missing_step(user: dict[str, Any] | None) -> str | None:
    """Ro'yxatdan o'tishda yetishmayotgan qadam."""
    if not user or not user.get("lang"):
        return "lang"
    if not user.get("phone"):
        return "phone"
    if not user.get("name"):
        return "name"
    if not user.get("pref_type"):
        return "address"
    return None


def valid_name(text: str | None) -> str | None:
    name = " ".join((text or "").split())
    if not 2 <= len(name) <= 40 or name.startswith("/") or sum(ch.isalpha() for ch in name) < 2:
        return None
    return name


def normalize_phone(text: str | None) -> str | None:
    text = (text or "").strip()
    if not PHONE_RE.match(text):
        return None
    digits = "".join(c for c in text if c.isdigit())
    if len(digits) == 9:  # mahalliy format: 90 123 45 67
        digits = "998" + digits
    if not 11 <= len(digits) <= 15:
        return None
    return "+" + digits


def clean_address(text: str | None) -> str | None:
    address = " ".join((text or "").split())
    if not ADDRESS_MIN <= len(address) <= ADDRESS_MAX or address.startswith("/"):
        return None
    return address


def _has_webapp(ctx: AppContext) -> bool:
    return ctx.settings.public_url.startswith("https://")


def _kb(ctx: AppContext, lang: str, user_id: int):
    return main_keyboard(lang, admin=ctx.is_panel_admin(user_id))


async def _lang(ctx: AppContext, user_id: int) -> str:
    user = await ctx.db.get_user(user_id)
    return norm_lang(user.get("lang") if user else None)


def _label(b: dict[str, Any], lang: str) -> str:
    return b["name"].get(lang) or b["name"].get("uz") or b["id"]


def _store_as_branch(ctx: AppContext) -> dict[str, Any]:
    """Filiallar kiritilmagan bo'lsa — do'konning o'zi bitta filial sifatida."""
    s = ctx.catalog.store
    name = s.get("name", "")
    return {"id": "", "name": {"uz": name, "ru": name}, "address": s.get("address") or {},
            "phone": s.get("phone", ""), "hours": s.get("hours") or {"open": "00:00", "close": "00:00"},
            "location": s.get("location"), "active": True}


def _branches(ctx: AppContext) -> list[dict[str, Any]]:
    return ctx.catalog.active_branches() or [_store_as_branch(ctx)]


def _user_branch(ctx: AppContext, user: dict[str, Any]) -> dict[str, Any]:
    chosen = ctx.catalog.branch(user.get("branch_id"))
    if chosen and chosen["active"]:
        return chosen
    return _branches(ctx)[0]


def _contact_phone(ctx: AppContext, order: dict[str, Any]) -> str:
    branch = ctx.catalog.branch(order.get("branch_id"))
    return (branch or {}).get("phone") or ctx.catalog.store.get("phone", "")


def _saved_address(user: dict[str, Any]) -> str:
    if user.get("last_address"):
        return user["last_address"]
    if user.get("last_lat") is not None and user.get("last_lon") is not None:
        return coords_text(user["last_lat"], user["last_lon"])
    return ""


def _status_prefix(ctx: AppContext, lang: str) -> str:
    if not ctx.catalog.store.get("accepting", True):
        return t(lang, "paused_now") + "\n\n"
    if not ctx.catalog.is_open():
        return t(lang, "closed_now") + "\n\n"
    return ""


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


# =====================================================================  so'rovlar va panel
async def ask_step(ctx: AppContext, chat_id: int, user: dict[str, Any], step: str, *, edit: bool = False) -> None:
    """Qadamni so'raydi. edit=True — sozlamalardan o'zgartirish («Orqaga» tugmasi bilan)."""
    lang = norm_lang(user.get("lang"))
    send = ctx.bot.send_message
    if step == "lang":
        await send(chat_id, t("uz", "choose_lang"), reply_markup=lang_keyboard())
    elif step == "phone":
        await send(chat_id, t(lang, "ask_phone_edit" if edit else "ask_phone"), reply_markup=phone_keyboard(lang, back=edit))
    elif step == "name":
        tg_name = valid_name(user.get("first_name"))
        suggestion = tg_name if tg_name and tg_name != user.get("name") else None
        await send(chat_id, t(lang, "ask_name_edit" if edit else "ask_name"),
                   reply_markup=name_keyboard(lang, suggestion, back=edit))
    elif step == "address":
        s = ctx.catalog.store
        delivery = s.get("delivery", {}).get("enabled", True)
        pickup = s.get("pickup", {}).get("enabled", True)
        if not delivery:
            await choose_pickup(ctx, chat_id, user)
            return
        text = t(lang, "ask_location_edit" if edit else "ask_location") + t(lang, "ask_location_other")
        if pickup:
            text += t(lang, "ask_location_pickup")
        await send(chat_id, text, reply_markup=location_keyboard(lang, delivery, pickup, back=edit))


async def ask_location(ctx: AppContext, chat_id: int, lang: str) -> None:
    """Mini App «📍 Lokatsiyani yuborish» bosilganda (web.api_request_location) chaqiriladi."""
    user = await ctx.db.get_user(chat_id) or {"id": chat_id}
    await ask_step(ctx, chat_id, {**user, "lang": lang}, "address", edit=True)


async def send_welcome(ctx: AppContext, chat_id: int, user: dict[str, Any], back: bool = False) -> None:
    lang = norm_lang(user.get("lang"))
    s = ctx.catalog.store
    text = t(lang, "welcome_back" if back else "welcome",
             name=escape(user.get("name") or user.get("first_name") or ""),
             store=escape(s.get("name", "")), tagline=escape(s.get("tagline", {}).get(lang, "")))
    await ctx.bot.send_message(chat_id, text.rstrip(" —\n"), reply_markup=_kb(ctx, lang, user["id"]))
    await send_order_panel(ctx, chat_id, user)


async def send_order_panel(ctx: AppContext, chat_id: int, user: dict[str, Any], checkout: bool = False,
                           state: FSMContext | None = None) -> None:
    """Saqlangan manzil (yoki filial) + «Menyuni ochish» va uni o'zgartirish tugmalari."""
    lang = norm_lang(user.get("lang"))
    s = ctx.catalog.store
    delivery_on = s.get("delivery", {}).get("enabled", True)
    pickup_on = s.get("pickup", {}).get("enabled", True)
    order_type = user.get("pref_type") or ("delivery" if delivery_on else "pickup")
    if order_type == "delivery" and not delivery_on:
        order_type = "pickup"
    elif order_type == "pickup" and not pickup_on:
        order_type = "delivery"

    if order_type == "delivery":
        address = _saved_address(user)
        if not address:
            if state:
                await state.set_state(Edit.address)
            await ask_step(ctx, chat_id, user, "address", edit=True)
            return
        head = t(lang, "panel_delivery", address=escape(address))
    else:
        b = _user_branch(ctx, user)
        head = t(lang, "panel_pickup", branch=escape(_label(b, lang)), address=escape(b["address"].get(lang, "")))

    text = _status_prefix(ctx, lang) + head + t(lang, "continue_order" if checkout else "panel_hint")
    if not _has_webapp(ctx):
        await ctx.bot.send_message(chat_id, text + "\n\n⚠️ PUBLIC_URL (https) sozlanmagan — Mini App ochilmaydi.")
        return
    await ctx.bot.send_message(chat_id, text, reply_markup=order_panel_keyboard(
        lang, ctx.settings.webapp_url, order_type, checkout,
        can_switch=delivery_on and pickup_on, multi_branch=len(ctx.catalog.active_branches()) > 1,
    ))


async def _finish(ctx: AppContext, chat_id: int, uid: int, onboarding: bool, head: str, panel: bool) -> None:
    """Profil o'zgargandan keyin: keyingi qadam, xush kelibsiz yoki tasdiq + buyurtma paneli."""
    user = await ctx.db.get_user(uid) or {"id": uid}
    lang = norm_lang(user.get("lang"))
    if panel and uid in ctx.location_requests:
        # Mini App ichidan so'ralgan — to'g'ridan-to'g'ri rasmiylashtirishga qaytaramiz
        ctx.location_requests.discard(uid)
        await ctx.bot.send_message(chat_id, head, reply_markup=_kb(ctx, lang, uid))
        await send_order_panel(ctx, chat_id, user, checkout=True)
        return
    step = missing_step(user)
    if step:
        await ask_step(ctx, chat_id, user, step)
        return
    if onboarding:
        await _set_menu_button(ctx, uid, lang)
        await send_welcome(ctx, chat_id, user)
        return
    await ctx.bot.send_message(chat_id, head, reply_markup=_kb(ctx, lang, uid))
    if panel:
        await send_order_panel(ctx, chat_id, user)


async def _onboarding(ctx: AppContext, uid: int) -> bool:
    return missing_step(await ctx.db.get_user(uid)) is not None


# =====================================================================  saqlash
async def save_phone(message: Message, ctx: AppContext, state: FSMContext, phone: str) -> None:
    u = message.from_user
    await ctx.db.upsert_user(u.id, u.first_name, u.username)
    onboarding = await _onboarding(ctx, u.id)
    await ctx.db.set_user_field(u.id, "phone", phone)
    await state.clear()
    lang = await _lang(ctx, u.id)
    await _finish(ctx, message.chat.id, u.id, onboarding, t(lang, "phone_saved"), panel=False)


async def save_name(message: Message, ctx: AppContext, state: FSMContext, text: str | None) -> None:
    u = message.from_user
    lang = await _lang(ctx, u.id)
    name = valid_name(text)
    if not name:
        await message.answer(t(lang, "bad_name"))
        return
    onboarding = await _onboarding(ctx, u.id)
    await ctx.db.set_user_field(u.id, "name", name)
    await state.clear()
    await _finish(ctx, message.chat.id, u.id, onboarding, t(lang, "name_saved", name=escape(name)), panel=False)


async def save_typed_address(message: Message, ctx: AppContext, state: FSMContext, text: str | None) -> None:
    u = message.from_user
    lang = await _lang(ctx, u.id)
    address = clean_address(text)
    if not address:
        await message.answer(t(lang, "bad_address"))
        return
    await ctx.db.upsert_user(u.id, u.first_name, u.username)
    onboarding = await _onboarding(ctx, u.id)
    await ctx.db.set_typed_address(u.id, address)
    await state.clear()
    await _finish(ctx, message.chat.id, u.id, onboarding, t(lang, "location_saved", address=escape(address)), panel=True)


async def save_pickup(ctx: AppContext, chat_id: int, uid: int, branch_id: str | None,
                      state: FSMContext | None = None) -> None:
    onboarding = await _onboarding(ctx, uid)
    await ctx.db.set_user_field(uid, "pref_type", "pickup")
    await ctx.db.set_user_field(uid, "branch_id", branch_id or None)
    if state:
        await state.clear()
    user = await ctx.db.get_user(uid) or {}
    lang = norm_lang(user.get("lang"))
    b = _user_branch(ctx, user)
    head = t(lang, "pickup_chosen", branch=escape(_label(b, lang)), address=escape(b["address"].get(lang, "")))
    await _finish(ctx, chat_id, uid, onboarding, head, panel=True)


async def choose_pickup(ctx: AppContext, chat_id: int, user: dict[str, Any], state: FSMContext | None = None) -> None:
    """Bir nechta filial bo'lsa — tanlatadi, bitta bo'lsa — darhol saqlaydi."""
    lang = norm_lang(user.get("lang"))
    branches = ctx.catalog.active_branches()
    if len(branches) > 1:
        open_ids = {b["id"] for b in branches if ctx.catalog.branch_open(b)}
        await ctx.bot.send_message(chat_id, t(lang, "choose_branch"),
                                   reply_markup=branches_keyboard(lang, branches, open_ids))
        return
    await save_pickup(ctx, chat_id, user["id"], branches[0]["id"] if branches else None, state)


async def use_saved_delivery(ctx: AppContext, chat_id: int, uid: int, state: FSMContext) -> None:
    user = await ctx.db.get_user(uid) or {"id": uid}
    if not _saved_address(user):
        await state.set_state(Edit.address)
        await ask_step(ctx, chat_id, user, "address", edit=True)
        return
    await ctx.db.set_user_field(uid, "pref_type", "delivery")
    await state.clear()
    user = await ctx.db.get_user(uid)
    if uid in ctx.location_requests:
        ctx.location_requests.discard(uid)
        await send_order_panel(ctx, chat_id, user, checkout=True)
        return
    await send_order_panel(ctx, chat_id, user)


# =====================================================================  start va til
@router.message(CommandStart())
async def cmd_start(message: Message, ctx: AppContext, state: FSMContext) -> None:
    await state.clear()
    u = message.from_user
    await ctx.db.upsert_user(u.id, u.first_name, u.username)
    user = await ctx.db.get_user(u.id)
    step = missing_step(user)
    if step:
        await ask_step(ctx, message.chat.id, user, step)
        return
    await _set_menu_button(ctx, u.id, norm_lang(user["lang"]))
    await send_welcome(ctx, message.chat.id, user, back=True)


@router.callback_query(F.data.startswith("lang:"))
async def cb_lang(call: CallbackQuery, ctx: AppContext) -> None:
    lang = norm_lang(call.data.split(":", 1)[1])
    u = call.from_user
    await ctx.db.upsert_user(u.id, u.first_name, u.username)
    await ctx.db.set_user_field(u.id, "lang", lang)
    await _set_menu_button(ctx, u.id, lang)
    user = await ctx.db.get_user(u.id)
    step = missing_step(user)
    await call.answer(t(lang, "lang_saved"))
    try:
        greet = t(lang, "greet", store=escape(ctx.catalog.store.get("name", "")))
        await call.message.edit_text(greet if step else t(lang, "lang_saved"))
    except Exception:
        pass
    if step:
        await ask_step(ctx, call.message.chat.id, user, step)
    else:
        await ctx.bot.send_message(call.message.chat.id, t(lang, "home_menu"), reply_markup=_kb(ctx, lang, u.id))


# =====================================================================  kontakt va lokatsiya
@router.message(F.contact)
async def on_contact(message: Message, ctx: AppContext, state: FSMContext) -> None:
    lang = await _lang(ctx, message.from_user.id)
    contact = message.contact
    if contact.user_id and contact.user_id != message.from_user.id:
        await message.answer(t(lang, "phone_not_own"), reply_markup=phone_keyboard(lang))
        return
    digits = "".join(c for c in contact.phone_number if c.isdigit())
    await save_phone(message, ctx, state, "+" + digits)


@router.message(F.location)
async def on_location(message: Message, ctx: AppContext, state: FSMContext) -> None:
    u = message.from_user
    lang = await _lang(ctx, u.id)
    lat, lon = round(message.location.latitude, 6), round(message.location.longitude, 6)
    address = message.venue.address if message.venue else None
    address = address or await reverse_geocode(lat, lon, lang, ctx.settings.public_url) or coords_text(lat, lon)
    await ctx.db.upsert_user(u.id, u.first_name, u.username)
    onboarding = await _onboarding(ctx, u.id)
    await ctx.db.set_location(u.id, lat, lon, address)
    await state.clear()
    await _finish(ctx, message.chat.id, u.id, onboarding, t(lang, "location_saved", address=escape(address)), panel=True)


# =====================================================================  asosiy menyu tugmalari
@router.message(F.text.in_(all_variants("btn_order")))
async def on_order(message: Message, ctx: AppContext, state: FSMContext) -> None:
    await state.clear()
    u = message.from_user
    await ctx.db.upsert_user(u.id, u.first_name, u.username)
    user = await ctx.db.get_user(u.id)
    step = missing_step(user)
    if step:
        await ask_step(ctx, message.chat.id, user, step)
        return
    await send_order_panel(ctx, message.chat.id, user, state=state)


@router.message(F.text.in_(all_variants("btn_pickup_self")))
async def on_pickup(message: Message, ctx: AppContext, state: FSMContext) -> None:
    await state.clear()
    u = message.from_user
    await ctx.db.upsert_user(u.id, u.first_name, u.username)
    await choose_pickup(ctx, message.chat.id, await ctx.db.get_user(u.id), state)


@router.message(F.text.in_(all_variants("btn_prev_address")))
async def on_prev_address(message: Message, ctx: AppContext, state: FSMContext) -> None:
    # eski klaviaturadagi tugma
    await use_saved_delivery(ctx, message.chat.id, message.from_user.id, state)


@router.message(F.text.in_(all_variants("btn_back") | all_variants("btn_skip")))
async def on_back(message: Message, ctx: AppContext, state: FSMContext) -> None:
    await state.clear()
    uid = message.from_user.id
    ctx.location_requests.discard(uid)
    user = await ctx.db.get_user(uid)
    step = missing_step(user)
    if step:
        await ask_step(ctx, message.chat.id, user or {"id": uid}, step)
        return
    lang = norm_lang(user.get("lang"))
    await message.answer(t(lang, "home_menu"), reply_markup=_kb(ctx, lang, uid))


@router.message(F.text.in_(all_variants("btn_my_orders")))
async def on_my_orders(message: Message, ctx: AppContext, state: FSMContext) -> None:
    await state.clear()
    uid = message.from_user.id
    lang = await _lang(ctx, uid)
    orders = await ctx.db.user_orders(uid, limit=5)
    if not orders:
        await message.answer(t(lang, "no_orders"))
        user = await ctx.db.get_user(uid)
        if not missing_step(user):
            await send_order_panel(ctx, message.chat.id, user, state=state)
        return
    blocks = [t(lang, "my_orders_title")] + [user_order_short(o, lang) for o in orders]
    base = ctx.settings.webapp_url if _has_webapp(ctx) else None
    await message.answer("\n\n".join(blocks), reply_markup=my_orders_keyboard(lang, base, orders))


def _branch_block(ctx: AppContext, b: dict[str, Any], lang: str) -> str:
    h = b["hours"]
    hours = t(lang, "hours_24") if h["open"] == h["close"] else f"{h['open']}–{h['close']}"
    text = t(lang, "branch_item", name=escape(_label(b, lang)),
             state=t(lang, "state_open" if ctx.catalog.branch_open(b) else "state_closed"),
             address=escape(b["address"].get(lang, "") or "—"), hours=hours)
    if b.get("phone"):
        text += t(lang, "branch_phone", phone=escape(b["phone"]))
    loc = b.get("location")
    if isinstance(loc, dict) and loc.get("lat") is not None and loc.get("lon") is not None:
        text += t(lang, "branch_map", url=f"https://maps.google.com/?q={loc['lat']},{loc['lon']}")
    return text


@router.message(F.text.in_(all_variants("btn_branches") | all_variants("btn_about")))
async def on_branches(message: Message, ctx: AppContext, state: FSMContext) -> None:
    await state.clear()
    lang = await _lang(ctx, message.from_user.id)
    s = ctx.catalog.store
    parts = [t(lang, "about", store=escape(s.get("name", "")), about=escape(s.get("about", {}).get(lang, ""))).rstrip()]
    parts.append(t(lang, "branches_title"))
    parts += [_branch_block(ctx, b, lang) for b in _branches(ctx)]
    await message.answer("\n\n".join(parts), disable_web_page_preview=True)


@router.message(F.text.in_(all_variants("btn_contacts")))
async def on_contacts(message: Message, ctx: AppContext, state: FSMContext) -> None:
    await state.clear()
    lang = await _lang(ctx, message.from_user.id)
    s = ctx.catalog.store
    lines = [t(lang, "contacts_line", name=escape(_label(b, lang)), phone=escape(b["phone"]))
             for b in _branches(ctx) if b.get("phone")]
    text = t(lang, "contacts", phones="\n".join(lines) or escape(s.get("phone") or "—"))
    if s.get("support_username"):
        text += t(lang, "contacts_tg", username=escape(s["support_username"].lstrip("@")))
    if s.get("instagram"):
        text += t(lang, "contacts_ig", instagram=escape(s["instagram"].lstrip("@")))
    await message.answer(text, disable_web_page_preview=True)


@router.message(F.text.in_(all_variants("btn_settings")))
async def on_settings(message: Message, ctx: AppContext, state: FSMContext) -> None:
    await state.clear()
    user = await ctx.db.get_user(message.from_user.id) or {}
    lang = norm_lang(user.get("lang"))
    if user.get("pref_type") == "pickup":
        address = t(lang, "settings_pickup", branch=_label(_user_branch(ctx, user), lang))
    else:
        address = _saved_address(user) or t(lang, "not_set")
    await message.answer(
        t(lang, "settings", name=escape(user.get("name") or t(lang, "not_set")),
          phone=escape(user.get("phone") or t(lang, "not_set")), address=escape(address)),
        reply_markup=settings_keyboard(lang),
    )


# =====================================================================  inline tugmalar
@router.callback_query(F.data == "settings:lang")
async def cb_settings_lang(call: CallbackQuery) -> None:
    await call.answer()
    await call.message.answer(t("uz", "choose_lang"), reply_markup=lang_keyboard())


@router.callback_query(F.data.in_({"settings:phone", "settings:name", "settings:address", "addr:change"}))
async def cb_edit(call: CallbackQuery, ctx: AppContext, state: FSMContext) -> None:
    step = {"settings:phone": "phone", "settings:name": "name"}.get(call.data, "address")
    await call.answer()
    await state.set_state({"phone": Edit.phone, "name": Edit.name, "address": Edit.address}[step])
    user = await ctx.db.get_user(call.from_user.id) or {"id": call.from_user.id}
    await ask_step(ctx, call.message.chat.id, user, step, edit=True)


@router.callback_query(F.data.in_({"type:pickup", "branch:pick"}))
async def cb_to_pickup(call: CallbackQuery, ctx: AppContext, state: FSMContext) -> None:
    await call.answer()
    await state.clear()
    user = await ctx.db.get_user(call.from_user.id) or {"id": call.from_user.id}
    await choose_pickup(ctx, call.message.chat.id, user, state)


@router.callback_query(F.data == "type:delivery")
async def cb_to_delivery(call: CallbackQuery, ctx: AppContext, state: FSMContext) -> None:
    await call.answer()
    await use_saved_delivery(ctx, call.message.chat.id, call.from_user.id, state)


@router.callback_query(F.data.startswith("pb:"))
async def cb_pick_branch(call: CallbackQuery, ctx: AppContext, state: FSMContext) -> None:
    branch = ctx.catalog.branch(call.data[3:])
    if not branch or not branch["active"]:
        await call.answer("?")
        user = await ctx.db.get_user(call.from_user.id) or {"id": call.from_user.id}
        await choose_pickup(ctx, call.message.chat.id, user, state)
        return
    await call.answer()
    try:
        await call.message.edit_reply_markup(reply_markup=None)
    except Exception:
        pass
    await save_pickup(ctx, call.message.chat.id, call.from_user.id, branch["id"], state)


def _order_id(data: str) -> int | None:
    raw = data.split(":", 1)[1] if ":" in data else ""
    return int(raw) if raw.isdigit() else None


@router.callback_query(F.data.startswith("uc:"))
async def cb_cancel_ask(call: CallbackQuery, ctx: AppContext) -> None:
    lang = await _lang(ctx, call.from_user.id)
    oid = _order_id(call.data)
    order = await ctx.db.get_order(oid) if oid else None
    if order is None or order["user_id"] != call.from_user.id:
        await call.answer("?")
        return
    if order["status"] != "new":
        await call.answer(t(lang, "cannot_cancel", id=oid, phone=_contact_phone(ctx, order)), show_alert=True)
        return
    await call.answer()
    await call.message.answer(t(lang, "cancel_confirm", id=oid), reply_markup=cancel_confirm_keyboard(lang, oid))


@router.callback_query(F.data.startswith("ucy:"))
async def cb_cancel_yes(call: CallbackQuery, ctx: AppContext) -> None:
    lang = await _lang(ctx, call.from_user.id)
    oid = _order_id(call.data)
    order = await ctx.db.get_order(oid) if oid else None
    if order is None or order["user_id"] != call.from_user.id:
        await call.answer("?")
        return
    await call.answer()
    if await ctx.db.cancel_by_customer(oid, call.from_user.id):
        await call.message.edit_text(t(lang, "cancelled_by_you", id=oid))
        await customer_cancelled(ctx, await ctx.db.get_order(oid))
    else:
        await call.message.edit_text(t(lang, "cannot_cancel", id=oid, phone=escape(_contact_phone(ctx, order))))


@router.callback_query(F.data == "ucn")
async def cb_cancel_no(call: CallbackQuery, ctx: AppContext) -> None:
    await call.answer()
    await call.message.edit_text(t(await _lang(ctx, call.from_user.id), "kept"))


@router.callback_query(F.data.startswith("rate:"))
async def cb_rate(call: CallbackQuery, ctx: AppContext, state: FSMContext) -> None:
    parts = call.data.split(":")
    if len(parts) != 3 or not parts[1].isdigit() or parts[2] not in ("1", "2", "3", "4", "5"):
        await call.answer()
        return
    oid, score = int(parts[1]), int(parts[2])
    uid = call.from_user.id
    lang = await _lang(ctx, uid)
    try:
        await call.message.edit_reply_markup(reply_markup=None)
    except Exception:
        pass
    if not await ctx.db.set_rating(oid, uid, score):
        await call.answer(t(lang, "rate_already"))
        return
    await call.answer(t(lang, "rate_thanks", stars=stars(score)))
    await customer_rated(ctx, await ctx.db.get_order(oid))
    if score <= 3:
        await state.set_state(Edit.feedback)
        await state.update_data(order_id=oid)
        await call.message.answer(t(lang, "ask_feedback"), reply_markup=skip_keyboard(lang))
    else:
        await call.message.answer(t(lang, "rate_thanks", stars=stars(score)) + "\n" + t(lang, "rate_thanks_full"),
                                  reply_markup=_kb(ctx, lang, uid))


# =====================================================================  holatdagi matnlar
@router.message(Edit.phone, F.text)
async def on_phone_text(message: Message, ctx: AppContext, state: FSMContext) -> None:
    phone = normalize_phone(message.text)
    if not phone:
        await message.answer(t(await _lang(ctx, message.from_user.id), "bad_phone"))
        return
    await save_phone(message, ctx, state, phone)


@router.message(Edit.name, F.text)
async def on_name_text(message: Message, ctx: AppContext, state: FSMContext) -> None:
    await save_name(message, ctx, state, message.text)


@router.message(Edit.address, F.text)
async def on_address_text(message: Message, ctx: AppContext, state: FSMContext) -> None:
    await save_typed_address(message, ctx, state, message.text)


@router.message(Edit.feedback, F.text)
async def on_feedback(message: Message, ctx: AppContext, state: FSMContext) -> None:
    data = await state.get_data()
    await state.clear()
    uid = message.from_user.id
    lang = await _lang(ctx, uid)
    text = " ".join(message.text.split())[:500]
    oid = data.get("order_id")
    if oid and text and await ctx.db.set_feedback(oid, uid, text):
        order = await ctx.db.get_order(oid)
        await notify_staff(ctx, order, at(ctx.settings.admin_lang, "feedback_note", id=oid,
                                          name=escape(order.get("name") or "—"), text=escape(text)))
    await message.answer(t(lang, "feedback_thanks"), reply_markup=_kb(ctx, lang, uid))


# =====================================================================  qolgan hammasi
@router.message()
async def fallback(message: Message, ctx: AppContext, state: FSMContext) -> None:
    uid = message.from_user.id
    user = await ctx.db.get_user(uid)
    text = message.text or ""
    if text and not text.startswith("/"):
        if uid in ctx.location_requests and clean_address(text):
            # Mini App lokatsiya so'radi, mijoz esa manzilni yozib yubordi
            await save_typed_address(message, ctx, state, text)
            return
        # Ro'yxatdan o'tish qadamlari holatsiz: profildagi bo'sh joyga qarab javobni qabul qilamiz
        step = missing_step(user)
        if step == "phone" and normalize_phone(text):
            await save_phone(message, ctx, state, normalize_phone(text))
            return
        if step == "name":
            await save_name(message, ctx, state, text)
            return
        if step == "address":
            await save_typed_address(message, ctx, state, text)
            return
    step = missing_step(user)
    if step:
        await ask_step(ctx, message.chat.id, user or {"id": uid}, step)
        return
    lang = norm_lang(user.get("lang"))
    await message.answer(t(lang, "unknown"), reply_markup=_kb(ctx, lang, uid))
