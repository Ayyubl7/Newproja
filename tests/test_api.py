"""Mini App API va buyurtma holatlari testi (Telegram'ga ulanmasdan)."""
import asyncio
import hashlib
import hmac
import json
import time
from pathlib import Path
from urllib.parse import urlencode

import pytest
from aiogram import Bot
from aiohttp.test_utils import TestClient, TestServer

import bot.web as web_module
from bot.catalog import Catalog
from bot.config import Settings
from tests.conftest import FIXTURES as DATA_DIR
from bot.context import AppContext
from bot.db import Database
from bot.orders import TRANSITIONS, admin_keyboard, admin_text, can_transition, user_order_created_text
from bot.seed import ensure_seeded
from bot.web import build_web_app

TOKEN = "123456:TEST-token_for_tests"


def make_init_data(user_id: int = 42, token: str = TOKEN, auth_date: int | None = None) -> str:
    fields = {
        "auth_date": str(auth_date or int(time.time())),
        "query_id": "AAH",
        "user": json.dumps({"id": user_id, "first_name": "Ali", "username": "ali", "language_code": "uz"}),
    }
    check = "\n".join(f"{k}={v}" for k, v in sorted(fields.items()))
    secret = hmac.new(b"WebAppData", token.encode(), hashlib.sha256).digest()
    fields["hash"] = hmac.new(secret, check.encode(), hashlib.sha256).hexdigest()
    return urlencode(fields)


def make_settings(tmp: Path, **over) -> Settings:
    base = dict(
        bot_token=TOKEN, admin_chat_id=-100123, admin_ids=frozenset(), admin_lang="uz",
        public_url="https://example.com", host="127.0.0.1", port=0, db_path=tmp / "t.db",
        webhook_secret="s" * 32, mode="web", dev_mode=False, dev_user_id=0,
    )
    base.update(over)
    return Settings(**base)


ORDER = {
    "items": [{"id": "classic", "qty": 2}, {"id": "cola", "qty": 1}],
    "type": "delivery", "address": "Chilonzor 9, 12-uy", "lat": 41.28, "lon": 69.2,
    "name": "Ali", "phone": "+998 90 123 45 67", "comment": "domofon <b>yo'q</b>",
    "payment": "cash", "lang": "uz",
    # mijoz "narx" yuborsa ham e'tiborga olinmaydi
    "price": 1,
}


def run(coro):
    return asyncio.run(coro)


async def _client(tmp: Path, announced: list, **over):
    settings = make_settings(tmp, **over)
    db = Database(settings.db_path)
    await db.connect()
    await ensure_seeded(db, DATA_DIR)
    store = await db.get_setting("store")
    store["hours"] = {"open": "00:00", "close": "00:00"}  # 24/7 — test vaqtiga bog'liq bo'lmasin
    await db.set_setting("store", store)
    ctx = AppContext(settings=settings, bot=Bot(TOKEN), db=db, catalog=await Catalog.from_db(db))
    await ctx.reload_admins()

    async def fake_announce(_ctx, order_id):
        announced.append(order_id)

    web_module.announce_new_order = fake_announce
    web_module._last_order_at.clear()
    client = TestClient(TestServer(build_web_app(ctx)))
    await client.start_server()
    return client, ctx


async def _close(client, ctx):
    await client.close()
    await ctx.db.close()
    await ctx.bot.session.close()


def auth(user_id=42):
    return {"Authorization": "tma " + make_init_data(user_id)}


def test_bootstrap_requires_valid_signature(tmp_path):
    async def go():
        client, ctx = await _client(tmp_path, [])
        try:
            assert (await client.get("/api/bootstrap")).status == 401
            bad = {"Authorization": "tma " + make_init_data(token="999:other")}
            assert (await client.get("/api/bootstrap", headers=bad)).status == 401
            old = {"Authorization": "tma " + make_init_data(auth_date=int(time.time()) - 3 * 86400)}
            assert (await client.get("/api/bootstrap", headers=old)).status == 401
            r = await client.get("/api/bootstrap", headers=auth())
            assert r.status == 200
            data = await r.json()
            assert data["store"]["name"] == "Ayva Burgers"
            assert len(data["menu"]["products"]) == len(ctx.catalog.products)
        finally:
            await _close(client, ctx)
    run(go())


def test_order_happy_path_and_server_side_pricing(tmp_path):
    announced = []

    async def go():
        client, ctx = await _client(tmp_path, announced)
        try:
            r = await client.post("/api/order", json=ORDER, headers=auth())
            assert r.status == 200, await r.text()
            data = await r.json()
            oid = data["order"]["id"]
            assert oid == 1001
            assert data["order"]["total"] == 32000 * 2 + 10000 + 10000  # + yetkazish
            await asyncio.sleep(0)
            assert announced == [oid]

            order = await ctx.db.get_order(oid)
            assert order["status"] == "new" and order["user_id"] == 42
            assert order["lat"] == 41.28 and order["address"] == "Chilonzor 9, 12-uy"
            user = await ctx.db.get_user(42)
            assert user["phone"] == "+998 90 123 45 67" and user["last_address"] == "Chilonzor 9, 12-uy"

            # matnlarda foydalanuvchi kiritgan HTML qochirilgan bo'lishi kerak
            text = admin_text(ctx, order, user)
            assert "&lt;b&gt;" in text and "<b>yo'q</b>" not in text
            assert "yandex.uz/maps" in text
            assert "#1001" in user_order_created_text(ctx, order)

            # 15 soniya ichida ikkinchi buyurtma — rad
            r2 = await client.post("/api/order", json=ORDER, headers=auth())
            assert r2.status == 429
        finally:
            await _close(client, ctx)
    run(go())


@pytest.mark.parametrize("patch, code", [
    ({"phone": "123"}, "bad_phone"),
    ({"address": "x", "lat": None, "lon": None}, "bad_address"),
    ({"payment": "click"}, "payment_unavailable"),
    ({"type": "teleport"}, "bad_type"),
    ({"items": [{"id": "water", "qty": 1}]}, "min_order"),
    ({"lat": 41.2, "lon": None}, "bad_location"),
    ({"lat": "41.2", "lon": 69}, "bad_location"),
    ({"comment": "a" * 301}, "too_long"),
])
def test_order_validation(tmp_path, patch, code):
    async def go():
        client, ctx = await _client(tmp_path, [])
        try:
            r = await client.post("/api/order", json={**ORDER, **patch}, headers=auth())
            assert r.status in (400, 409), await r.text()
            assert (await r.json())["error"] == code
        finally:
            await _close(client, ctx)
    run(go())


def test_closed_store_rejects_orders(tmp_path):
    async def go():
        client, ctx = await _client(tmp_path, [])
        ctx.catalog.is_open = lambda now=None: False
        try:
            r = await client.post("/api/order", json=ORDER, headers=auth())
            assert r.status == 409 and (await r.json())["error"] == "closed"
        finally:
            await _close(client, ctx)
    run(go())


def test_pickup_ignores_address(tmp_path):
    async def go():
        client, ctx = await _client(tmp_path, [])
        try:
            body = {**ORDER, "type": "pickup", "address": "", "lat": None, "lon": None}
            r = await client.post("/api/order", json=body, headers=auth(7))
            assert r.status == 200
            order = await ctx.db.get_order((await r.json())["order"]["id"])
            assert order["delivery_fee"] == 0 and order["address"] is None
        finally:
            await _close(client, ctx)
    run(go())


def test_status_transitions(tmp_path):
    async def go():
        db = Database(tmp_path / "s.db")
        await db.connect()
        try:
            base = {"user_id": 1, "items": [], "subtotal": 1, "delivery_fee": 0, "total": 1,
                    "phone": "+998901234567", "payment": "cash", "lang": "uz"}
            oid = await db.create_order({**base, "type": "delivery"})
            order = await db.get_order(oid)
            assert can_transition(order, "accepted")
            assert not can_transition(order, "done")
            assert await db.update_status(oid, "new", "accepted")
            # ikkinchi admin eski holatdan bossa — o'zgarmaydi
            assert not await db.update_status(oid, "new", "cancelled")
            order = await db.get_order(oid)
            assert can_transition(order, "on_the_way") and not can_transition(order, "ready")

            pid = await db.create_order({**base, "type": "pickup"})
            await db.update_status(pid, "new", "accepted")
            porder = await db.get_order(pid)
            assert can_transition(porder, "ready") and not can_transition(porder, "on_the_way")
            assert set(TRANSITIONS) == {"new", "accepted", "on_the_way", "ready"}
        finally:
            await db.close()
    run(go())


def test_admin_keyboard_per_status(tmp_path):
    settings = make_settings(tmp_path)
    ctx = AppContext(settings=settings, bot=None, db=None, catalog=Catalog({}, [], {}))  # type: ignore[arg-type]
    order = {"id": 5, "type": "delivery", "status": "new"}
    kb = admin_keyboard(ctx, order)
    assert [b.callback_data for b in kb.inline_keyboard[0]] == ["o:5:accepted", "o:5:ask_cancel"]
    order["status"] = "accepted"
    assert admin_keyboard(ctx, order).inline_keyboard[0][0].callback_data == "o:5:on_the_way"
    order["status"] = "done"
    assert admin_keyboard(ctx, order) is None


def test_delivery_with_telegram_location_only(tmp_path):
    async def go():
        client, ctx = await _client(tmp_path, [])
        try:
            body = {**ORDER, "address": "", "lat": 40.5286, "lon": 70.9425}
            r = await client.post("/api/order", json=body, headers=auth(9))
            assert r.status == 200, await r.text()
            order = await ctx.db.get_order((await r.json())["order"]["id"])
            assert order["address"].startswith("📍 40.52860") and order["lat"] == 40.5286
            boot = await (await client.get("/api/bootstrap", headers=auth(9))).json()
            assert boot["profile"]["lat"] == 40.5286 and boot["profile"]["type"] == "delivery"
            # ikkinchi buyurtma podyezd bilan — saqlangan manzil o'zgarmaydi
            web_module._last_order_at.clear()
            saved = boot["profile"]["address"]
            body2 = {**body, "address": saved + " — 2-podyezd"}
            assert (await client.post("/api/order", json=body2, headers=auth(9))).status == 200
            boot = await (await client.get("/api/bootstrap", headers=auth(9))).json()
            assert boot["profile"]["address"] == saved
        finally:
            await _close(client, ctx)
    run(go())


def test_branches_in_order_api(tmp_path):
    from datetime import datetime, timedelta

    from bot.catalog import TASHKENT_TZ

    async def go():
        client, ctx = await _client(tmp_path, [])
        try:
            now = datetime.now(TASHKENT_TZ)
            later = (now + timedelta(hours=2)).strftime("%H:%M"), (now + timedelta(hours=3)).strftime("%H:%M")
            await ctx.db.create_branch("late", {"name_uz": "Kechki", "open": later[0], "close": later[1]})
            await ctx.db.create_branch("north", {"name_uz": "Shimoliy", "open": "00:00", "close": "00:00",
                                                 "lat": 41.35, "lon": 69.3})
            await ctx.reload_catalog()

            r = await client.post("/api/order", json={**ORDER, "type": "pickup", "branch_id": "late"}, headers=auth())
            assert r.status == 409 and (await r.json())["error"] == "branch_closed"
            r = await client.post("/api/order", json={**ORDER, "branch_id": "nope"}, headers=auth())
            assert r.status == 400 and (await r.json())["error"] == "bad_branch"
            r = await client.post("/api/order", json={**ORDER, "payment": "card"}, headers=auth())
            assert r.status == 400 and (await r.json())["error"] == "payment_unavailable"

            # olib ketish — tanlangan filial; ism, tur va filial profilda eslab qolinadi
            r = await client.post("/api/order", json={**ORDER, "type": "pickup", "branch_id": "north", "name": "Vali"},
                                  headers=auth())
            body = await r.json()
            assert r.status == 200 and body["order"]["branch"]["uz"] == "Shimoliy"
            assert (await ctx.db.get_order(body["order"]["id"]))["branch_id"] == "north"
            boot = await (await client.get("/api/bootstrap", headers=auth())).json()
            prof = boot["profile"]
            assert (prof["name"], prof["branch_id"], prof["type"]) == ("Vali", "north", "pickup")
            assert [b["id"] for b in boot["store"]["branches"]] == ["main", "late", "north"]
            assert [b["is_open"] for b in boot["store"]["branches"]] == [True, False, True]
            assert boot["store"]["payments"] == {"cash": True}

            # yetkazib berish — koordinatasi bor eng yaqin ochiq filial
            web_module._last_order_at.clear()
            r = await client.post("/api/order", json=ORDER, headers=auth())
            assert (await ctx.db.get_order((await r.json())["order"]["id"]))["branch_id"] == "north"
            assert (await ctx.db.get_user(42))["pref_type"] == "delivery"

            # yozilgan manzil (lokatsiyasiz) profilga saqlanadi, eski nuqta o'chadi
            web_module._last_order_at.clear()
            r = await client.post("/api/order", json={**ORDER, "lat": None, "lon": None, "address": "Navoiy ko'chasi 5"},
                                  headers=auth())
            assert r.status == 200
            u = await ctx.db.get_user(42)
            assert (u["last_address"], u["last_lat"]) == ("Navoiy ko'chasi 5", None)
        finally:
            await _close(client, ctx)
    run(go())


def test_my_orders_and_customer_cancel(tmp_path, monkeypatch):
    async def go():
        client, ctx = await _client(tmp_path, [])
        cancelled = []

        async def fake_cancelled(_ctx, order):
            cancelled.append(order["id"])

        monkeypatch.setattr(web_module, "customer_cancelled", fake_cancelled)
        try:
            r = await client.post("/api/order", json=ORDER, headers=auth())
            oid = (await r.json())["order"]["id"]
            orders = (await (await client.get("/api/my-orders", headers=auth())).json())["orders"]
            assert [o["id"] for o in orders] == [oid]
            assert orders[0]["can_cancel"] and orders[0]["items"][0]["id"] == "classic"
            assert orders[0]["branch"]["uz"] == "Ayva Burgers"

            # boshqa mijoz ko'rmaydi va bekor qilolmaydi
            assert (await (await client.get("/api/my-orders", headers=auth(43))).json())["orders"] == []
            assert (await client.post(f"/api/my-orders/{oid}/cancel", headers=auth(43))).status == 404
            assert (await client.get("/api/my-orders")).status == 401

            r = await client.post(f"/api/my-orders/{oid}/cancel", headers=auth())
            assert r.status == 200 and (await r.json())["order"]["status"] == "cancelled"
            await asyncio.sleep(0.01)
            assert cancelled == [oid]
            r = await client.post(f"/api/my-orders/{oid}/cancel", headers=auth())
            assert r.status == 409 and (await r.json())["error"] == "cannot_cancel"
        finally:
            await _close(client, ctx)
    run(go())
