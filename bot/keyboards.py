"""Mijoz uchun tugmalar."""
from __future__ import annotations

from typing import Any

from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    WebAppInfo,
)

from .texts import ADMIN_PANEL_BUTTON, t


def webapp_url(base_url: str, lang: str, **params: Any) -> str:
    query = "&".join(f"{k}={v}" for k, v in {"lang": lang, **params}.items() if v)
    return f"{base_url}?{query}"


def lang_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="🇺🇿 O'zbekcha", callback_data="lang:uz"),
        InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang:ru"),
    ]])


def _reply(rows: list[list[KeyboardButton]]) -> ReplyKeyboardMarkup | ReplyKeyboardRemove:
    rows = [r for r in rows if r]
    if not rows:
        return ReplyKeyboardRemove()
    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True, one_time_keyboard=True)


def phone_keyboard(lang: str, back: bool = False) -> ReplyKeyboardMarkup:
    rows = [[KeyboardButton(text=t(lang, "btn_share_phone"), request_contact=True)]]
    if back:
        rows.append([KeyboardButton(text=t(lang, "btn_back"))])
    return _reply(rows)


def name_keyboard(lang: str, suggestion: str | None, back: bool = False) -> ReplyKeyboardMarkup | ReplyKeyboardRemove:
    """Ism so'ralganda — Telegram'dagi ismni bir bosishda yuborish tugmasi."""
    rows = [[KeyboardButton(text=suggestion)]] if suggestion else []
    if back:
        rows.append([KeyboardButton(text=t(lang, "btn_back"))])
    return _reply(rows)


def location_keyboard(lang: str, delivery: bool = True, pickup: bool = True,
                      back: bool = False) -> ReplyKeyboardMarkup | ReplyKeyboardRemove:
    rows = []
    if delivery:
        rows.append([KeyboardButton(text=t(lang, "btn_send_location"), request_location=True)])
    last = []
    if pickup:
        last.append(KeyboardButton(text=t(lang, "btn_pickup_self")))
    if back:
        last.append(KeyboardButton(text=t(lang, "btn_back")))
    rows.append(last)
    return _reply(rows)


def skip_keyboard(lang: str) -> ReplyKeyboardMarkup:
    return _reply([[KeyboardButton(text=t(lang, "btn_skip"))]])


def main_keyboard(lang: str, admin: bool = False) -> ReplyKeyboardMarkup:
    rows = [
        [KeyboardButton(text=t(lang, "btn_order"))],
        [KeyboardButton(text=t(lang, "btn_my_orders")), KeyboardButton(text=t(lang, "btn_branches"))],
        [KeyboardButton(text=t(lang, "btn_contacts")), KeyboardButton(text=t(lang, "btn_settings"))],
    ]
    if admin:
        rows.append([KeyboardButton(text=ADMIN_PANEL_BUTTON)])
    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True, is_persistent=True)


def order_panel_keyboard(lang: str, base_url: str, order_type: str, checkout: bool = False,
                         can_switch: bool = True, multi_branch: bool = False) -> InlineKeyboardMarkup:
    """Buyurtma paneli: Mini App tugmasi + manzil/turini o'zgartirish.

    Inline web_app tugmasi — Mini App'ga initData uzatiladi (reply tugmada bunday emas).
    """
    text = t(lang, "btn_continue_order") if checkout else t(lang, "btn_open_menu")
    url = webapp_url(base_url, lang, type=order_type, to="checkout" if checkout else "")
    rows = [[InlineKeyboardButton(text=text, web_app=WebAppInfo(url=url))]]
    extra = []
    if order_type == "delivery":
        extra.append(InlineKeyboardButton(text=t(lang, "btn_change_address"), callback_data="addr:change"))
        if can_switch:
            extra.append(InlineKeyboardButton(text=t(lang, "btn_to_pickup"), callback_data="type:pickup"))
    else:
        if can_switch:
            extra.append(InlineKeyboardButton(text=t(lang, "btn_to_delivery"), callback_data="type:delivery"))
        if multi_branch:
            extra.append(InlineKeyboardButton(text=t(lang, "btn_change_branch"), callback_data="branch:pick"))
    if extra:
        rows.append(extra)
    return InlineKeyboardMarkup(inline_keyboard=rows)


def branches_keyboard(lang: str, branches: list[dict[str, Any]], open_ids: set[str]) -> InlineKeyboardMarkup:
    rows = []
    for b in branches:
        label = f"🏪 {b['name'].get(lang) or b['id']}"
        if b["id"] not in open_ids:
            label += " · " + t(lang, "state_closed")
        rows.append([InlineKeyboardButton(text=label, callback_data=f"pb:{b['id']}")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def settings_keyboard(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t(lang, "btn_set_name"), callback_data="settings:name"),
         InlineKeyboardButton(text=t(lang, "btn_set_phone"), callback_data="settings:phone")],
        [InlineKeyboardButton(text=t(lang, "btn_set_address"), callback_data="settings:address"),
         InlineKeyboardButton(text=t(lang, "btn_set_lang"), callback_data="settings:lang")],
    ])


def my_orders_keyboard(lang: str, base_url: str | None, orders: list[dict[str, Any]]) -> InlineKeyboardMarkup | None:
    rows = []
    for i, o in enumerate(orders):
        row = []
        if o["status"] == "new":
            row.append(InlineKeyboardButton(text=t(lang, "btn_cancel_order", id=o["id"]),
                                            callback_data=f"uc:{o['id']}"))
        if base_url and i < 3:
            row.append(InlineKeyboardButton(text=t(lang, "btn_repeat", id=o["id"]),
                                            web_app=WebAppInfo(url=webapp_url(base_url, lang, repeat=o["id"]))))
        if row:
            rows.append(row)
    return InlineKeyboardMarkup(inline_keyboard=rows) if rows else None


def cancel_keyboard(lang: str, order_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text=t(lang, "btn_cancel_order", id=order_id), callback_data=f"uc:{order_id}"),
    ]])


def cancel_confirm_keyboard(lang: str, order_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text=t(lang, "btn_yes_cancel"), callback_data=f"ucy:{order_id}"),
        InlineKeyboardButton(text=t(lang, "btn_no"), callback_data="ucn"),
    ]])
