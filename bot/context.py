"""Ilova bo'ylab umumiy obyektlar (bot, baza, menyu, sozlamalar)."""
from __future__ import annotations

import asyncio
from collections.abc import Coroutine
from dataclasses import dataclass
from typing import Any

from aiogram import Bot

from .catalog import Catalog
from .config import Settings
from .db import Database


@dataclass
class AppContext:
    settings: Settings
    bot: Bot
    db: Database
    catalog: Catalog

    def is_admin(self, user_id: int | None, chat_id: int | None = None) -> bool:
        if user_id is not None and user_id in self.settings.admin_ids:
            return True
        return chat_id is not None and chat_id != 0 and chat_id == self.settings.admin_chat_id


_background: set[asyncio.Task] = set()


def spawn(coro: Coroutine[Any, Any, Any]) -> asyncio.Task:
    """Fon vazifasini ishga tushiradi va GC o'chirib yubormasligi uchun havolani saqlaydi."""
    task = asyncio.create_task(coro)
    _background.add(task)
    task.add_done_callback(_background.discard)
    return task
