"""Mijoz uchun tugmalar."""
from __future__ import annotations

from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    WebAppInfo,
)

from .texts import ADMIN_PANEL_BUTTON, t


def webapp_url(base_url: str, lang: str, **params: str) -> str:
    query = "&".join(f"{k}={v}" for k, v in {"lang": lang, **params}.items() if v)
    return f"{base_url}?{query}"


def lang_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="🇺🇿 O'zbekcha", callback_data="lang:uz"),
        InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang:ru"),
    ]])


def phone_keyboard(lang: str) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=t(lang, "btn_share_phone"), request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def main_keyboard(lang: str, admin: bool = False) -> ReplyKeyboardMarkup:
    rows = [
        [KeyboardButton(text=t(lang, "btn_order"))],
        [KeyboardButton(text=t(lang, "btn_my_orders")), KeyboardButton(text=t(lang, "btn_about"))],
        [KeyboardButton(text=t(lang, "btn_contacts")), KeyboardButton(text=t(lang, "btn_settings"))],
    ]
    if admin:
        rows.append([KeyboardButton(text=ADMIN_PANEL_BUTTON)])
    return ReplyKeyboardMarkup(
        keyboard=rows,
        resize_keyboard=True,
        is_persistent=True,
    )


def open_menu_keyboard(lang: str, base_url: str, order_type: str = "", checkout: bool = False) -> InlineKeyboardMarkup:
    # Inline web_app tugmasi — Mini App'ga initData uzatiladi (reply tugmada bunday emas).
    text = t(lang, "btn_continue_order") if checkout else t(lang, "btn_open_menu")
    url = webapp_url(base_url, lang, type=order_type, to="checkout" if checkout else "")
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=text, web_app=WebAppInfo(url=url))]])


def location_keyboard(lang: str, has_saved: bool, delivery: bool = True, pickup: bool = True) -> ReplyKeyboardMarkup:
    rows = []
    if delivery:
        rows.append([KeyboardButton(text=t(lang, "btn_send_location"), request_location=True)])
        if has_saved:
            rows.append([KeyboardButton(text=t(lang, "btn_prev_address"))])
    last = [KeyboardButton(text=t(lang, "btn_back"))]
    if pickup:
        last.insert(0, KeyboardButton(text=t(lang, "btn_pickup_self")))
    rows.append(last)
    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True, one_time_keyboard=True)


def settings_keyboard(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t(lang, "btn_change_lang"), callback_data="settings:lang")],
        [InlineKeyboardButton(text=t(lang, "btn_change_phone"), callback_data="settings:phone")],
    ])
