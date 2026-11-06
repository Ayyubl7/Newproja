"""Mijozlarga ommaviy xabar yuborish (Telegram limitlariga rioya qilgan holda)."""
from __future__ import annotations

import asyncio
import logging
import time
from collections.abc import Awaitable, Callable
from typing import Any

from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError, TelegramRetryAfter

from .context import AppContext, spawn

log = logging.getLogger(__name__)

Sender = Callable[[int, str], Awaitable[None]]
Reporter = Callable[[dict[str, Any]], Awaitable[None]]


def start_broadcast(ctx: AppContext, sender: Sender, report: Reporter | None = None) -> bool:
    """Fonda yuborishni boshlaydi. Boshqa yuborish ketayotgan bo'lsa — False."""
    if ctx.broadcast.get("running"):
        return False
    ctx.broadcast = {"running": True, "total": 0, "ok": 0, "fail": 0, "started_at": time.time()}
    spawn(_run(ctx, sender, report))
    return True


async def _run(ctx: AppContext, sender: Sender, report: Reporter | None) -> None:
    st = ctx.broadcast
    try:
        users = await ctx.db.all_users_lang()
        st["total"] = len(users)
        for uid, lang in users:
            for _ in range(3):
                try:
                    await sender(uid, lang or "uz")
                    st["ok"] += 1
                    break
                except TelegramRetryAfter as e:
                    await asyncio.sleep(e.retry_after + 0.5)
                except (TelegramForbiddenError, TelegramBadRequest):
                    st["fail"] += 1  # botni bloklagan yoki chat topilmadi
                    break
                except Exception:
                    log.exception("Broadcast xatosi (user=%s)", uid)
                    st["fail"] += 1
                    break
            await asyncio.sleep(0.04)  # ~25 xabar/soniya — Telegram limiti 30
    finally:
        st["running"] = False
        st["finished_at"] = time.time()
        if report:
            try:
                await report(st)
            except Exception:
                log.exception("Broadcast hisobotini yuborib bo'lmadi")
