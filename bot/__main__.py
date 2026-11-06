"""Ishga tushirish: python -m bot"""
from __future__ import annotations

import asyncio
import logging
import signal

from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import (
    BotCommand,
    BotCommandScopeAllPrivateChats,
    BotCommandScopeChat,
    MenuButtonWebApp,
    WebAppInfo,
)
from aiogram.webhook.aiohttp_server import SimpleRequestHandler

from .catalog import Catalog
from .config import DATA_DIR, Settings, load_settings
from .context import AppContext
from .db import Database
from .handlers import build_router
from .web import build_web_app

log = logging.getLogger("ayva")


async def setup_bot_ui(bot: Bot, settings: Settings) -> None:
    await bot.set_my_commands([BotCommand(command="start", description="Menyu / Меню")],
                              scope=BotCommandScopeAllPrivateChats())
    if settings.admin_chat_id:
        try:
            await bot.set_my_commands([
                BotCommand(command="active", description="Faol buyurtmalar"),
                BotCommand(command="stats", description="Statistika"),
                BotCommand(command="stoplist", description="Stop-list"),
                BotCommand(command="reload", description="Menyuni qayta yuklash"),
                BotCommand(command="broadcast", description="Reklama (reply qilib)"),
                BotCommand(command="admin", description="Yordam"),
            ], scope=BotCommandScopeChat(chat_id=settings.admin_chat_id))
        except Exception:
            log.warning("Admin guruhi uchun buyruqlarni o'rnatib bo'lmadi — bot guruhga qo'shilganmi?")
    if settings.public_url.startswith("https://"):
        await bot.set_chat_menu_button(menu_button=MenuButtonWebApp(
            text="Menyu", web_app=WebAppInfo(url=settings.webapp_url)))


async def _wait_for_stop() -> None:
    stop = asyncio.Event()
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, stop.set)
        except NotImplementedError:  # Windows
            pass
    await stop.wait()


async def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    settings = load_settings()

    bot = Bot(settings.bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    db = Database(settings.db_path)
    await db.connect()
    catalog = Catalog.load(DATA_DIR)
    catalog.stoplist = await db.stoplist()
    ctx = AppContext(settings=settings, bot=bot, db=db, catalog=catalog)

    dp = Dispatcher()
    dp["ctx"] = ctx
    dp.include_router(build_router())

    app = build_web_app(ctx)
    if settings.use_webhook:
        SimpleRequestHandler(dispatcher=dp, bot=bot, secret_token=settings.webhook_secret).register(
            app, path=settings.webhook_path)

    runner = web.AppRunner(app, access_log=None)
    await runner.setup()
    await web.TCPSite(runner, settings.host, settings.port).start()
    log.info("Web server: http://%s:%s  (Mini App: %s)", settings.host, settings.port,
             settings.webapp_url if settings.public_url else "PUBLIC_URL yo'q")

    try:
        if settings.mode == "web":
            log.warning("BOT_MODE=web: faqat Mini App serveri ishlayapti, Telegram'ga ulanilmadi")
            await _wait_for_stop()
            return
        await setup_bot_ui(bot, settings)
        if settings.use_webhook:
            await bot.set_webhook(
                url=settings.public_url + settings.webhook_path,
                secret_token=settings.webhook_secret,
                allowed_updates=dp.resolve_used_update_types(),
            )
            log.info("Webhook rejimi: %s", settings.public_url)
            await _wait_for_stop()
        else:
            log.info("Polling rejimi (lokal sinov uchun)")
            await bot.delete_webhook(drop_pending_updates=False)
            await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await runner.cleanup()
        await db.close()
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
