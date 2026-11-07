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
from bot.orders import OrderCb, announce_new_order, notify_user_status
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
    dp.storage.storage.clear()  # FSM holatlari testlar orasida o'tib ketmasin
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
            await complete_profile(ctx, pref_type="pickup")

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


def cbq(data, uid=USER_ID, chat_id=USER_ID):
    return CallbackQuery(id="9", from_user=user(uid), chat_instance="c", data=data,
                         message=msg("x", chat_id=chat_id, uid=uid))


def sent(session, chat_id=USER_ID):
    return [c for c in session.calls if type(c).__name__ == "SendMessage" and c.chat_id == chat_id]


async def complete_profile(ctx, **extra):
    await ctx.db.upsert_user(USER_ID, "Ali", "ali")
    fields = {"lang": "uz", "phone": "+998901112233", "name": "Ali", **extra}
    for k, v in fields.items():
        await ctx.db.set_user_field(USER_ID, k, v)


def order_data(**over):
    data = {
        "user_id": USER_ID, "items": [{"id": "classic", "name": {"uz": "Klassik", "ru": "Классик"},
                                       "price": 32000, "qty": 1}],
        "subtotal": 32000, "delivery_fee": 10000, "total": 42000, "type": "delivery",
        "address": "Chilonzor", "lat": None, "lon": None, "phone": "+998901112233", "name": "Ali",
        "comment": None, "payment": "cash", "lang": "uz",
    }
    data.update(over)
    return data


def test_onboarding_flow(tmp_path):
    async def go():
        dp, bot, session, ctx = await setup(tmp_path)
        try:
            await feed(dp, bot, message=msg("/start"))
            assert session.calls[-1].text.startswith("🇺🇿 Tilni tanlang")

            session.calls.clear()
            await feed(dp, bot, callback_query=cbq("lang:ru"))
            assert "SetChatMenuButton" in session.names()
            assert (await ctx.db.get_user(USER_ID))["lang"] == "ru"
            assert "1/3" in session.calls[-1].text and "номер телефона" in session.calls[-1].text

            # 1/3 telefon -> 2/3 ism (Telegram'dagi ism — bir bosishda)
            session.calls.clear()
            await feed(dp, bot, message=msg(contact=Contact(phone_number="998901112233", first_name="Ali",
                                                            user_id=USER_ID)))
            assert (await ctx.db.get_user(USER_ID))["phone"] == "+998901112233"
            last = session.calls[-1]
            assert "2/3" in last.text and last.reply_markup.keyboard[0][0].text == "Ali"

            # boshqa odamning kontakti qabul qilinmaydi
            await feed(dp, bot, message=msg(contact=Contact(phone_number="1", first_name="X", user_id=999)))
            assert (await ctx.db.get_user(USER_ID))["phone"] == "+998901112233"

            # noto'g'ri ism -> qayta; to'g'ri ism -> 3/3 manzil
            session.calls.clear()
            await feed(dp, bot, message=msg("7"))
            assert "буквами" in session.calls[-1].text
            await feed(dp, bot, message=msg("Алишер"))
            assert (await ctx.db.get_user(USER_ID))["name"] == "Алишер"
            kb = session.calls[-1].reply_markup
            assert "3/3" in session.calls[-1].text and kb.keyboard[0][0].request_location is True
            assert [b.text for b in kb.keyboard[-1]] == ["🛍 Заберу сам"]  # ro'yxatdan o'tishda «Orqaga» yo'q

            # manzil yozib yuborildi -> xush kelibsiz + manzil bilan menyu paneli
            session.calls.clear()
            await feed(dp, bot, message=msg("ул. Навои 12, ориентир школа"))
            u = await ctx.db.get_user(USER_ID)
            assert (u["last_address"], u["pref_type"], u["last_lat"]) == ("ул. Навои 12, ориентир школа", "delivery", None)
            out = sent(session)
            assert "Готово, Алишер" in out[0].text and out[0].reply_markup.keyboard[0][0].text == "🍔 Заказать"
            panel = out[-1]
            assert "ул. Навои 12" in panel.text
            assert "type=delivery" in panel.reply_markup.inline_keyboard[0][0].web_app.url
            assert [b.callback_data for b in panel.reply_markup.inline_keyboard[1]] == ["addr:change", "type:pickup"]

            # keyingi /start — hammasi eslab qolingan
            session.calls.clear()
            await feed(dp, bot, message=msg("/start"))
            out = sent(session)
            assert "С возвращением, Алишер" in out[0].text and "ул. Навои 12" in out[-1].text

            session.calls.clear()
            await feed(dp, bot, message=msg("📦 Мои заказы"))
            assert "нет заказов" in session.calls[0].text

            session.calls.clear()
            await feed(dp, bot, message=msg("🏪 Филиалы"))
            assert "Ayva Burgers" in session.calls[0].text and "24/7" in session.calls[0].text
            session.calls.clear()
            await feed(dp, bot, message=msg("ℹ️ О нас"))  # eski klaviatura tugmasi
            assert "Наши филиалы" in session.calls[0].text
        finally:
            await ctx.db.close()
    asyncio.run(go())


def test_location_pickup_and_settings(tmp_path, monkeypatch):
    import html

    import bot.handlers.user as user_mod
    from aiogram.types import Location

    async def fake_geocode(lat, lon, lang="uz", contact=""):
        return "Qo'qon, Navoiy ko'chasi, 12"

    monkeypatch.setattr(user_mod, "reverse_geocode", fake_geocode)

    def loc_msg(lat=40.5286, lon=70.9425):
        return msg().model_copy(update={"location": Location(latitude=lat, longitude=lon)})

    async def go():
        dp, bot, session, ctx = await setup(tmp_path)
        try:
            await complete_profile(ctx)

            # manzil hali yo'q -> «Buyurtma berish» 3/3 qadamni so'raydi
            await feed(dp, bot, message=msg("🍔 Buyurtma berish"))
            assert "3/3" in session.calls[-1].text
            assert session.calls[-1].reply_markup.keyboard[0][0].request_location is True

            # lokatsiya -> saqlanadi, xush kelibsiz + panel
            session.calls.clear()
            await feed(dp, bot, message=loc_msg())
            u = await ctx.db.get_user(USER_ID)
            assert (u["last_lat"], u["last_lon"], u["pref_type"]) == (40.5286, 70.9425, "delivery")
            panel = sent(session)[-1]
            assert "Navoiy ko'chasi" in html.unescape(panel.text)
            assert "type=delivery" in panel.reply_markup.inline_keyboard[0][0].web_app.url

            # keyingi safar — darhol saqlangan manzil bilan panel
            session.calls.clear()
            await feed(dp, bot, message=msg("🍔 Buyurtma berish"))
            assert len(sent(session)) == 1 and "Navoiy ko'chasi" in html.unescape(sent(session)[0].text)

            # Mini App ichidan so'ralgan lokatsiya -> «Buyurtmani davom ettirish» (to=checkout)
            ctx.location_requests.add(USER_ID)
            session.calls.clear()
            await feed(dp, bot, message=loc_msg(40.53, 70.95))
            btn = sent(session)[-1].reply_markup.inline_keyboard[0][0]
            assert btn.text == "🛒 Buyurtmani davom ettirish" and "to=checkout" in btn.web_app.url
            assert USER_ID not in ctx.location_requests

            # Mini App so'radi, mijoz esa manzilni yozib yubordi
            ctx.location_requests.add(USER_ID)
            session.calls.clear()
            await feed(dp, bot, message=msg("Turkiston ko'chasi 5, 2-podyezd"))
            assert (await ctx.db.get_user(USER_ID))["last_address"] == "Turkiston ko'chasi 5, 2-podyezd"
            assert "to=checkout" in sent(session)[-1].reply_markup.inline_keyboard[0][0].web_app.url

            # olib ketish: bir nechta filial -> tanlash
            await ctx.db.create_branch("north", {"name_uz": "Shimoliy", "address_uz": "Mustaqillik 1",
                                                 "open": "00:00", "close": "00:00"})
            await ctx.reload_catalog()
            session.calls.clear()
            await feed(dp, bot, callback_query=cbq("type:pickup"))
            rows = session.calls[-1].reply_markup.inline_keyboard
            assert [r[0].callback_data for r in rows] == ["pb:main", "pb:north"]
            session.calls.clear()
            await feed(dp, bot, callback_query=cbq("pb:north"))
            u = await ctx.db.get_user(USER_ID)
            assert (u["pref_type"], u["branch_id"]) == ("pickup", "north")
            panel = sent(session)[-1]
            assert "Shimoliy" in panel.text and "type=pickup" in panel.reply_markup.inline_keyboard[0][0].web_app.url
            assert [b.callback_data for b in panel.reply_markup.inline_keyboard[1]] == ["type:delivery", "branch:pick"]

            # yana yetkazib berishga — saqlangan manzil bilan
            session.calls.clear()
            await feed(dp, bot, callback_query=cbq("type:delivery"))
            assert (await ctx.db.get_user(USER_ID))["pref_type"] == "delivery"
            assert "Turkiston" in html.unescape(sent(session)[-1].text)

            # manzilni o'zgartirish (holat bilan): qisqa matn rad etiladi, to'g'risi saqlanadi
            session.calls.clear()
            await feed(dp, bot, callback_query=cbq("addr:change"))
            assert "⬅️ Orqaga" in [b.text for b in session.calls[-1].reply_markup.keyboard[-1]]
            await feed(dp, bot, message=msg("abc"))
            assert "juda qisqa" in session.calls[-1].text
            session.calls.clear()
            await feed(dp, bot, message=msg("Navoiy ko'chasi 77"))
            assert (await ctx.db.get_user(USER_ID))["last_address"] == "Navoiy ko'chasi 77"
            assert "type=delivery" in sent(session)[-1].reply_markup.inline_keyboard[0][0].web_app.url

            # ism va telefonni sozlamalardan o'zgartirish
            await feed(dp, bot, callback_query=cbq("settings:name"))
            await feed(dp, bot, message=msg("Vali"))
            assert (await ctx.db.get_user(USER_ID))["name"] == "Vali"
            await feed(dp, bot, callback_query=cbq("settings:phone"))
            await feed(dp, bot, message=msg("salom"))
            assert "noto'g'ri" in html.unescape(session.calls[-1].text)
            await feed(dp, bot, message=msg("90 765 43 21"))
            assert (await ctx.db.get_user(USER_ID))["phone"] == "+998907654321"
            session.calls.clear()
            await feed(dp, bot, message=msg("⚙️ Sozlamalar"))
            text = html.unescape(session.calls[-1].text)
            assert "Vali" in text and "+998907654321" in text and "Navoiy ko'chasi 77" in text

            # holat yo'q, profil to'liq — tushunarsiz matn
            session.calls.clear()
            await feed(dp, bot, message=msg("salom"))
            assert "menyudan tanlang" in session.calls[-1].text
        finally:
            await ctx.db.close()
    asyncio.run(go())


def test_customer_cancel_and_rating(tmp_path):
    async def go():
        dp, bot, session, ctx = await setup(tmp_path)
        try:
            await complete_profile(ctx, pref_type="delivery", last_address="Navoiy 1")
            oid = await ctx.db.create_order(order_data(branch_id="main"))
            await announce_new_order(ctx, oid)
            confirm = [c for c in sent(session) if f"#{oid}" in c.text][0]
            assert confirm.reply_markup.inline_keyboard[0][0].callback_data == f"uc:{oid}"

            # begona odam bekor qila olmaydi
            await feed(dp, bot, callback_query=cbq(f"ucy:{oid}", uid=77, chat_id=77))
            assert (await ctx.db.get_order(oid))["status"] == "new"

            session.calls.clear()
            await feed(dp, bot, callback_query=cbq(f"uc:{oid}"))
            assert [b.callback_data for b in session.calls[-1].reply_markup.inline_keyboard[0]] == [f"ucy:{oid}", "ucn"]
            session.calls.clear()
            await feed(dp, bot, callback_query=cbq(f"ucy:{oid}"))
            assert (await ctx.db.get_order(oid))["status"] == "cancelled"
            staff = [c for c in session.calls if getattr(c, "chat_id", None) == ADMIN_CHAT]
            assert any(type(c).__name__ == "EditMessageText" for c in staff)  # guruhdagi xabar yangilandi
            assert any("bekor qildi" in (getattr(c, "text", "") or "") for c in staff)

            # qabul qilingan buyurtmani mijoz bekor qilolmaydi
            oid2 = await ctx.db.create_order(order_data())
            await ctx.db.update_status(oid2, "new", "accepted")
            await feed(dp, bot, callback_query=cbq(f"ucy:{oid2}"))
            assert (await ctx.db.get_order(oid2))["status"] == "accepted"

            # yakunlangan buyurtma -> baho tugmalari
            await ctx.db.update_status(oid2, "accepted", "on_the_way")
            await ctx.db.update_status(oid2, "on_the_way", "done")
            session.calls.clear()
            await notify_user_status(ctx, await ctx.db.get_order(oid2))
            kb = session.calls[-1].reply_markup.inline_keyboard[0]
            assert [b.callback_data for b in kb] == [f"rate:{oid2}:{n}" for n in range(1, 6)]

            # begona odam baho qo'yolmaydi
            await feed(dp, bot, callback_query=cbq(f"rate:{oid2}:5", uid=77, chat_id=77))
            assert (await ctx.db.get_order(oid2))["rating"] is None

            # 2 yulduz -> guruhga xabar + izoh so'raladi
            session.calls.clear()
            await feed(dp, bot, callback_query=cbq(f"rate:{oid2}:2"))
            assert (await ctx.db.get_order(oid2))["rating"] == 2
            assert any(c.text.startswith("⭐⭐ —") for c in sent(session, ADMIN_CHAT))
            assert "Nima yoqmadi" in session.calls[-1].text
            session.calls.clear()
            await feed(dp, bot, message=msg("Burger sovuq edi"))
            assert (await ctx.db.get_order(oid2))["feedback"] == "Burger sovuq edi"
            assert any("sovuq" in c.text for c in sent(session, ADMIN_CHAT))
            # ikkinchi marta baho qo'yib bo'lmaydi
            await feed(dp, bot, callback_query=cbq(f"rate:{oid2}:5"))
            assert (await ctx.db.get_order(oid2))["rating"] == 2

            # «Buyurtmalarim»: takrorlash tugmasi (Mini App, repeat=ID)
            session.calls.clear()
            await feed(dp, bot, message=msg("📦 Buyurtmalarim"))
            rows = session.calls[-1].reply_markup.inline_keyboard
            assert f"repeat={oid2}" in rows[0][0].web_app.url
        finally:
            await ctx.db.close()
    asyncio.run(go())


def test_branch_routing_and_branch_group(tmp_path):
    async def go():
        dp, bot, session, ctx = await setup(tmp_path)
        try:
            branch_chat = -100777
            await ctx.db.create_branch("north", {"name_uz": "Shimoliy", "open": "00:00", "close": "00:00",
                                                 "chat_id": branch_chat})
            await ctx.reload_catalog()
            await ctx.db.upsert_user(USER_ID, "Ali", "ali")
            oid = await ctx.db.create_order(order_data(branch_id="north"))
            other = await ctx.db.create_order(order_data(branch_id="main"))
            await announce_new_order(ctx, oid)
            to_branch = sent(session, branch_chat)
            assert to_branch and "Shimoliy" in to_branch[0].text
            assert not sent(session, ADMIN_CHAT)
            assert (await ctx.db.get_order(oid))["admin_chat_id"] == branch_chat

            # filial guruhidagi xodim tugmani bosa oladi
            press = CallbackQuery(id="5", from_user=user(8), chat_instance="b",
                                  data=OrderCb(id=oid, action="accepted").pack(),
                                  message=msg("order", chat_id=branch_chat, uid=8))
            await feed(dp, bot, callback_query=press)
            assert (await ctx.db.get_order(oid))["status"] == "accepted"

            # /active filial guruhida — faqat o'z buyurtmalari, umumiy guruhda — hammasi
            session.calls.clear()
            await feed(dp, bot, message=msg("/active", chat_id=branch_chat, uid=8))
            text = session.calls[-1].text
            assert f"#{oid}" in text and f"#{other}" not in text
            session.calls.clear()
            await feed(dp, bot, message=msg("/active", chat_id=ADMIN_CHAT, uid=8))
            text = session.calls[-1].text
            assert f"#{oid}" in text and f"#{other}" in text and "Shimoliy" in text
            # filial guruhida statistika ham ochiq
            session.calls.clear()
            await feed(dp, bot, message=msg("/stats", chat_id=branch_chat, uid=8))
            assert "Statistika" in session.calls[-1].text
        finally:
            await ctx.db.close()
    asyncio.run(go())
