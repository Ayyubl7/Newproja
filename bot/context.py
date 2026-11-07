"""Ilova bo'ylab umumiy obyektlar (bot, baza, menyu, sozlamalar)."""
from __future__ import annotations

import asyncio
import secrets
import time
from collections.abc import Coroutine
from dataclasses import dataclass, field
from typing import Any

from aiogram import Bot

from .catalog import Catalog
from .config import Settings
from .db import Database

LOGIN_TOKEN_TTL = 10 * 60

# Rollar: owner — .env dagi ADMIN_IDS; admin — to'liq panel; cashier — buyurtmalar, stop-list va pauza
ROLES = ("admin", "cashier")
FULL_ROLES = ("owner", "admin")


@dataclass
class AppContext:
    settings: Settings
    bot: Bot
    db: Database
    catalog: Catalog
    # Admin paneldan qo'shilganlar: user_id -> rol (ADMIN_IDS — egalar, ular .env'da)
    extra_admins: dict[int, str] = field(default_factory=dict)
    # Kompyuterdan kirish uchun bir martalik havolalar: token -> (user_id, amal qilish muddati)
    login_tokens: dict[str, tuple[int, float]] = field(default_factory=dict)
    broadcast: dict[str, Any] = field(default_factory=lambda: {"running": False})
    # Mini App ichidan "lokatsiyani Telegram orqali yuborish" so'ragan mijozlar
    location_requests: set[int] = field(default_factory=set)

    # ---------- huquqlar ----------
    def is_owner(self, user_id: int | None) -> bool:
        return user_id is not None and user_id in self.settings.admin_ids

    def role_of(self, user_id: int | None) -> str | None:
        if user_id is None:
            return None
        if self.is_owner(user_id):
            return "owner"
        return self.extra_admins.get(user_id)

    def is_panel_admin(self, user_id: int | None) -> bool:
        return self.role_of(user_id) is not None

    def is_full_admin(self, user_id: int | None) -> bool:
        """Ega yoki administrator (kassir emas)."""
        return self.role_of(user_id) in FULL_ROLES

    def is_admin(self, user_id: int | None, chat_id: int | None = None) -> bool:
        """Buyurtma tugmalari va guruh buyruqlari: panel adminlari yoki admin guruhi a'zolari."""
        if self.is_panel_admin(user_id):
            return True
        return chat_id is not None and chat_id != 0 and chat_id in self.staff_chats()

    def branch_for_chat(self, chat_id: int | None) -> dict | None:
        """Filialning o'z guruhi bo'lsa — o'sha filial (guruhda faqat o'z buyurtmalari ko'rinadi)."""
        if not chat_id:
            return None
        return next((b for b in self.catalog.branches if b.get("chat_id") == chat_id), None)

    def staff_chats(self) -> set[int]:
        """Xodimlar guruhlari: umumiy ADMIN_CHAT_ID va filiallarning o'z guruhlari."""
        chats = {b["chat_id"] for b in self.catalog.branches if b.get("chat_id")}
        if self.settings.admin_chat_id:
            chats.add(self.settings.admin_chat_id)
        return chats

    async def reload_admins(self) -> None:
        self.extra_admins = {a["user_id"]: a["role"] if a["role"] in ROLES else "admin"
                             for a in await self.db.list_admins()}

    async def reload_catalog(self) -> None:
        # Yangi obyekt yaratib, bitta amal bilan almashtiramiz — so'rovlar hech qachon yarim holatni ko'rmaydi
        self.catalog = await Catalog.from_db(self.db)

    # ---------- bir martalik kirish havolasi ----------
    def new_login_token(self, user_id: int) -> str:
        now = time.time()
        for tok, (_, exp) in list(self.login_tokens.items()):
            if exp < now:
                self.login_tokens.pop(tok, None)
        token = secrets.token_urlsafe(24)
        self.login_tokens[token] = (user_id, now + LOGIN_TOKEN_TTL)
        return token

    def use_login_token(self, token: str) -> int | None:
        item = self.login_tokens.pop(token, None)
        if item is None or item[1] < time.time():
            return None
        return item[0]


_background: set[asyncio.Task] = set()


def spawn(coro: Coroutine[Any, Any, Any]) -> asyncio.Task:
    """Fon vazifasini ishga tushiradi va GC o'chirib yubormasligi uchun havolani saqlaydi."""
    task = asyncio.create_task(coro)
    _background.add(task)
    task.add_done_callback(_background.discard)
    return task
