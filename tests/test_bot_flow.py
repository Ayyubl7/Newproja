"""Bot suhbatini Telegram'siz sinash: so'rovlar soxta sessiyada yoziladi."""
import asyncio
from datetime import datetime, timezone
from pathlib import Path

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.base import BaseSession
from aiogram.enums import ParseMode
from aiogram.methods import TelegramMethod
from aiogram.methods import GetMe
from aiogram.types import CallbackQuery, Chat, Contact, Message, Update, User

from bot.catalog import Catalog
from tests.conftest import FIXTURES as DATA_DIR
from bot.context import AppContext
from bot.db import Database
from bot.handlers import build_router
from bot.orders import OrderCb, announce_new_order
from bot.seed import ensure_seeded

from .test_api import TOKEN, make_settings

ADMIN_CHAT = -100123
USER_ID = 42


class FakeSession(BaseSession):
    def __init__(self) -> None:
        super().__init__()
        self.calls: list[TelegramMethod] = []
        self._mid = 500

    async def make_request(self, bot, method, timeout=None):  # noqa: ANN001
        self.calls.append(method)
        if isinstance(method, GetMe):
            return User(id=1, is_bot=True, first_name="Ayva", username="ayvaburgers_bot")
        if method.__returning__ is Message:
            self._mid += 1
            chat_id = getattr(method, "chat_id", USER_ID)
            return Message(message_id=self._mid, date=datetime.now(timezone.utc),
                           chat=Chat(id=chat_id, type="private" if chat_id > 0 else "supergroup"),
                           text=getattr(method, "text", None))
        return True

    async def stream_content(self, *a, **kw):  # pragma: no cover
        raise NotImplementedError

    async def close(self) -> None:
        pass

    def names(self) -> list[str]:
        return [type(c).__name__ for c in self.calls]


def user(uid=USER_ID):
    return User(id=uid, is_bot=False, first_name="Ali", username="ali")


def msg(text=None, contact=None, chat_id=USER_ID, uid=USER_ID):
    chat = Chat(id=chat_id, type="private" if chat_id > 0 else "supergroup")
    return Message(message_id=1, date=datetime.now(timezone.utc), chat=chat, from_user=user(uid),
                   text=text, contact=contact)


async def setup(tmp: Path):
    session = FakeSession()
    bot = Bot(TOKEN, session=session, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    settings = make_settings(tmp, admin_chat_id=ADMIN_CHAT)
    db = Database(settings.db_path)
    await db.connect()
    await ensure_seeded(db, DATA_DIR)
    ctx = AppContext(settings=settings, bot=bot, db=db, catalog=await Catalog.from_db(db))
    dp = _dispatcher()
    dp["ctx"] = ctx
    return dp, bot, session, ctx


_DP: Dispatcher | None = None


def _dispatcher() -> Dispatcher:
    # Routerlar modul darajasida yagona — bitta Dispatcher'ga faqat bir marta ulanadi
    global _DP
    if _DP is None:
        _DP = Dispatcher()
        _DP.include_router(build_router())
    return _DP


async def feed(dp, bot, **kw):
    await dp.feed_update(bot, Update(update_id=1, **kw))


def test_onboarding_flow(tmp_path):
    async def go():
        dp, bot, session, ctx = await setup(tmp_path)
        try:
            await feed(dp, bot, message=msg("/start"))
            assert session.calls[-1].text.startswith("🇺🇿 Tilni tanlang")

            session.calls.clear()
            cb = CallbackQuery(id="1", from_user=user(), chat_instance="x", data="lang:ru",
                               message=msg("lang"))
            await feed(dp, bot, callback_query=cb)
            assert "SetChatMenuButton" in session.names()
            assert (await ctx.db.get_user(USER_ID))["lang"] == "ru"
            assert "номер телефона" in session.calls[-1].text

            session.calls.clear()
            await feed(dp, bot, message=msg(contact=Contact(phone_number="998901112233", first_name="Ali",
                                                            user_id=USER_ID)))
            assert (await ctx.db.get_user(USER_ID))["phone"] == "+998901112233"
            last = session.calls[-1]
            assert last.reply_markup.inline_keyboard[0][0].web_app.url == "https://example.com/?lang=ru"

            # boshqa odamning kontakti qabul qilinmaydi
            session.calls.clear()
            await feed(dp, bot, message=msg(contact=Contact(phone_number="1", first_name="X", user_id=999)))
            assert (await ctx.db.get_user(USER_ID))["phone"] == "+998901112233"

            session.calls.clear()
            await feed(dp, bot, message=msg("📦 Мои заказы"))
            assert "нет заказов" in session.calls[0].text

            session.calls.clear()
            await feed(dp, bot, message=msg("ℹ️ О нас"))
            assert "Ayva Burgers" in session.calls[0].text
        finally:
            await ctx.db.close()
    asyncio.run(go())


def test_admin_order_lifecycle(tmp_path):
    async def go():
        dp, bot, session, ctx = await setup(tmp_path)
        try:
            await ctx.db.upsert_user(USER_ID, "Ali", "ali")
            oid = await ctx.db.create_order({
                "user_id": USER_ID, "items": [{"id": "classic", "name": {"uz": "Klassik", "ru": "Классик"},
                                               "price": 32000, "qty": 1}],
                "subtotal": 32000, "delivery_fee": 10000, "total": 42000, "type": "delivery",
                "address": "Chilonzor", "lat": None, "lon": None, "phone": "+998901112233", "name": "Ali",
                "comment": None, "payment": "cash", "lang": "uz",
            })
            await announce_new_order(ctx, oid)
            to_admin = [c for c in session.calls if getattr(c, "chat_id", None) == ADMIN_CHAT]
            assert to_admin and "Yangi buyurtma #1001" in to_admin[0].text
            assert (await ctx.db.get_order(oid))["admin_message_id"] is not None
            assert any(getattr(c, "chat_id", None) == USER_ID and "#1001" in c.text for c in session.calls)

            def press(action, uid=7, chat=ADMIN_CHAT):
                m = msg("order", chat_id=chat, uid=uid)
                return CallbackQuery(id="2", from_user=user(uid), chat_instance="y",
                                     data=OrderCb(id=oid, action=action).pack(), message=m)

            # begona odam (shaxsiy chatdan) bosolmaydi
            session.calls.clear()
            await feed(dp, bot, callback_query=press("accepted", uid=99, chat=99))
            assert (await ctx.db.get_order(oid))["status"] == "new"

            for action in ("accepted", "on_the_way", "done"):
                session.calls.clear()
                await feed(dp, bot, callback_query=press(action))
                assert (await ctx.db.get_order(oid))["status"] == action
                notify = [c for c in session.calls if type(c).__name__ == "SendMessage"]
                assert notify and notify[0].chat_id == USER_ID

            # yakunlangan buyurtmani bekor qilib bo'lmaydi
            await feed(dp, bot, callback_query=press("cancelled"))
            assert (await ctx.db.get_order(oid))["status"] == "done"

            # admin buyruqlari
            session.calls.clear()
            await feed(dp, bot, message=msg("/stats", chat_id=ADMIN_CHAT, uid=7))
            assert "Statistika" in session.calls[-1].text
            await feed(dp, bot, message=msg("/stoplist", chat_id=ADMIN_CHAT, uid=7))
            assert "Stop-list" in session.calls[-1].text
            cb = CallbackQuery(id="3", from_user=user(7), chat_instance="z", data="sl:t:classic",
                               message=msg("sl", chat_id=ADMIN_CHAT, uid=7))
            await feed(dp, bot, callback_query=cb)
            assert not ctx.catalog.products["classic"]["available"]
            assert not (await ctx.db.get_product("classic"))["available"]

            # oddiy foydalanuvchi /stats yoza olmaydi
            session.calls.clear()
            await feed(dp, bot, message=msg("/stats"))
            assert all("Statistika" not in (getattr(c, "text", "") or "") for c in session.calls)
        finally:
            await ctx.db.close()
    asyncio.run(go())


def test_panel_command(tmp_path):
    async def go():
        dp, bot, session, ctx = await setup(tmp_path)
        ctx.settings = make_settings(tmp_path, admin_chat_id=ADMIN_CHAT, admin_ids=frozenset({USER_ID}))
        try:
            await ctx.db.upsert_user(USER_ID, "Ali", "ali")
            await ctx.db.set_user_field(USER_ID, "lang", "uz")
            await ctx.db.set_user_field(USER_ID, "phone", "+998901112233")

            # egasi: bosh menyuda "🛠 Admin panel" tugmasi bor
            await feed(dp, bot, message=msg("/start"))
            kb = next(c.reply_markup for c in session.calls if getattr(c, "reply_markup", None) is not None
                      and hasattr(c.reply_markup, "keyboard"))
            assert kb.keyboard[-1][0].text == "🛠 Admin panel"

            session.calls.clear()
            await feed(dp, bot, message=msg("🛠 Admin panel"))
            buttons = session.calls[-1].reply_markup.inline_keyboard
            assert buttons[0][0].web_app.url == "https://example.com/admin/"
            token = buttons[1][0].url.split("t=")[1]
            assert ctx.use_login_token(token) == USER_ID and ctx.use_login_token(token) is None

            # /start panel deep-link
            session.calls.clear()
            await feed(dp, bot, message=msg("/start panel"))
            assert session.calls[-1].reply_markup.inline_keyboard[0][0].web_app

            # begona odam — ruxsat yo'q va o'z ID'sini ko'radi
            session.calls.clear()
            await feed(dp, bot, message=msg("/panel", chat_id=55, uid=55))
            assert "55" in session.calls[-1].text and session.calls[-1].reply_markup is None

            # guruhda — shaxsiy chatga havola
            session.calls.clear()
            await feed(dp, bot, message=msg("/panel", chat_id=ADMIN_CHAT, uid=7))
            assert session.calls[-1].reply_markup.inline_keyboard[0][0].url == "https://t.me/ayvaburgers_bot?start=panel"
        finally:
            await ctx.db.close()
    asyncio.run(go())


def test_cashier_bot_permissions(tmp_path):
    async def go():
        dp, bot, session, ctx = await setup(tmp_path)
        try:
            await ctx.db.add_admin(USER_ID, "Kassa", "cashier")
            await ctx.reload_admins()
            await ctx.db.upsert_user(USER_ID, "Ali", "ali")
            # kassir panelni ocha oladi
            await feed(dp, bot, message=msg("/panel"))
            assert session.calls[-1].reply_markup.inline_keyboard[0][0].web_app
            # shaxsiy chatda statistika va reklama yo'q, stop-list bor
            for cmd in ("/stats", "/broadcast"):
                session.calls.clear()
                await feed(dp, bot, message=msg(cmd))
                assert all("Statistika" not in (getattr(c, "text", "") or "") and "📣" not in (getattr(c, "text", "") or "")
                           for c in session.calls), cmd
            session.calls.clear()
            await feed(dp, bot, message=msg("/stoplist"))
            assert "Stop-list" in session.calls[-1].text
            # admin guruhida statistika hamma xodimga ochiq
            session.calls.clear()
            await feed(dp, bot, message=msg("/stats", chat_id=ADMIN_CHAT, uid=USER_ID))
            assert "Statistika" in session.calls[-1].text
        finally:
            await ctx.db.close()
    asyncio.run(go())


def test_location_flow(tmp_path, monkeypatch):
    import bot.handlers.user as user_mod
    from aiogram.types import Location

    async def fake_geocode(lat, lon, lang="uz", contact=""):
        return "Qo'qon, Navoiy ko'chasi, 12"

    monkeypatch.setattr(user_mod, "reverse_geocode", fake_geocode)

    async def go():
        dp, bot, session, ctx = await setup(tmp_path)
        try:
            await ctx.db.upsert_user(USER_ID, "Ali", "ali")
            await ctx.db.set_user_field(USER_ID, "lang", "uz")
            await ctx.db.set_user_field(USER_ID, "phone", "+998901112233")

            # "Buyurtma berish" -> lokatsiya so'raladi (Telegram'ning o'z tugmasi)
            await feed(dp, bot, message=msg("🍔 Buyurtma berish"))
            kb = session.calls[-1].reply_markup
            assert kb.keyboard[0][0].request_location is True
            assert [b.text for b in kb.keyboard[-1]] == ["🛍 Olib ketaman", "⬅️ Orqaga"]

            # lokatsiya yuborildi -> manzil saqlanadi, menyu tugmasi keladi
            session.calls.clear()
            loc_msg = msg()
            loc_msg = loc_msg.model_copy(update={"location": Location(latitude=40.5286, longitude=70.9425)})
            await feed(dp, bot, message=loc_msg)
            user = await ctx.db.get_user(USER_ID)
            assert (user["last_lat"], user["last_lon"], user["pref_type"]) == (40.5286, 70.9425, "delivery")
            import html
            assert "Navoiy ko'chasi" in html.unescape(session.calls[0].text)
            url = session.calls[-1].reply_markup.inline_keyboard[0][0].web_app.url
            assert "type=delivery" in url and "to=checkout" not in url

            # keyingi safar "Oldingi manzil" tugmasi bor
            session.calls.clear()
            await feed(dp, bot, message=msg("🍔 Buyurtma berish"))
            assert session.calls[-1].reply_markup.keyboard[1][0].text == "🏠 Oldingi manzil"

            # Mini App ichidan so'ralgan bo'lsa — "Buyurtmani davom ettirish" (to=checkout)
            ctx.location_requests.add(USER_ID)
            session.calls.clear()
            await feed(dp, bot, message=msg("🏠 Oldingi manzil"))
            last = session.calls[-1].reply_markup.inline_keyboard[0][0]
            assert last.text == "🛒 Buyurtmani davom ettirish" and "to=checkout" in last.web_app.url
            assert USER_ID not in ctx.location_requests

            # olib ketish
            session.calls.clear()
            await feed(dp, bot, message=msg("🛍 Olib ketaman"))
            assert (await ctx.db.get_user(USER_ID))["pref_type"] == "pickup"
            assert "type=pickup" in session.calls[-1].reply_markup.inline_keyboard[0][0].web_app.url
        finally:
            await ctx.db.close()
    asyncio.run(go())
