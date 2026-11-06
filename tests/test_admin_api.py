"""Admin panel API testi: kirish, menyu, rasm, aksiyalar, sozlamalar, buyurtmalar, adminlar, xabar yuborish."""
import asyncio
from io import BytesIO

from aiogram import Bot
from aiohttp import FormData
from aiohttp.test_utils import TestClient, TestServer
from PIL import Image

import bot.web as web_module
from bot.catalog import Catalog
from bot.config import DATA_DIR
from bot.context import AppContext
from bot.db import Database
from bot.seed import ensure_seeded
from bot.web import build_web_app

from .test_api import ORDER, TOKEN, make_init_data, make_settings
from .test_bot_flow import FakeSession

OWNER = 42
STRANGER = 43


def run(coro):
    return asyncio.run(coro)


async def make_client(tmp, **over):
    settings = make_settings(tmp, admin_ids=frozenset({OWNER}), **over)
    db = Database(settings.db_path)
    await db.connect()
    await ensure_seeded(db, DATA_DIR)
    store = await db.get_setting("store")
    store["hours"] = {"open": "00:00", "close": "00:00"}
    await db.set_setting("store", store)
    session = FakeSession()
    ctx = AppContext(settings=settings, bot=Bot(TOKEN, session=session), db=db, catalog=await Catalog.from_db(db))
    await ctx.reload_admins()

    async def no_announce(_ctx, _oid):
        return None

    web_module.announce_new_order = no_announce
    web_module._last_order_at.clear()
    client = TestClient(TestServer(build_web_app(ctx)))
    await client.start_server()
    return client, ctx, session


async def close(client, ctx):
    await client.close()
    await ctx.db.close()


def tma(uid=OWNER):
    return {"Authorization": "tma " + make_init_data(uid)}


def png_bytes(size=(1600, 900), color=(240, 170, 20)):
    buf = BytesIO()
    Image.new("RGB", size, color).save(buf, "PNG")
    return buf.getvalue()


async def upload(client, data=None):
    form = FormData()
    form.add_field("file", data or png_bytes(), filename="photo.png", content_type="image/png")
    return await client.post("/api/admin/upload", data=form, headers=tma())


def test_auth_paths(tmp_path):
    async def go():
        # http test serveri — Secure cookie yuborilmaydi, shuning uchun public_url'siz
        client, ctx, _ = await make_client(tmp_path, public_url="")
        try:
            assert (await client.get("/api/admin/me")).status == 401
            r = await client.get("/api/admin/me", headers=tma(STRANGER))
            assert r.status == 403 and (await r.json())["user_id"] == STRANGER
            r = await client.get("/api/admin/me", headers=tma())
            assert r.status == 200 and (await r.json())["is_owner"] is True

            # kompyuter: bir martalik havola -> cookie
            token = ctx.new_login_token(OWNER)
            r = await client.get(f"/admin/login?t={token}", allow_redirects=False)
            assert r.status == 302 and r.headers["Location"] == "/admin/"
            assert "ayva_admin" in r.cookies
            assert (await client.get("/api/admin/me")).status == 200
            # cookie bilan o'zgartirish — X-Admin sarlavhasisiz rad etiladi (CSRF)
            body = {"name_uz": "Test"}
            assert (await client.post("/api/admin/categories", json=body)).status == 403
            assert (await client.post("/api/admin/categories", json=body, headers={"X-Admin": "1"})).status == 200
            # havola ikkinchi marta ishlamaydi
            client.session.cookie_jar.clear()
            r = await client.get(f"/admin/login?t={token}", allow_redirects=False)
            assert "expired" in r.headers["Location"]
            # soxta cookie
            client.session.cookie_jar.update_cookies({"ayva_admin": f"{OWNER}.9999999999.deadbeef"})
            assert (await client.get("/api/admin/me")).status == 401
            # panel sahifasi
            r = await client.get("/admin/")
            assert r.status == 200 and "Ayva" in await r.text()
        finally:
            await close(client, ctx)
    run(go())


def test_product_lifecycle_with_image_and_promo(tmp_path):
    async def go():
        client, ctx, _ = await make_client(tmp_path)
        try:
            r = await upload(client)
            assert r.status == 200, await r.text()
            url = (await r.json())["url"]
            path = ctx.settings.upload_dir / url.rsplit("/", 1)[1]
            with Image.open(path) as im:
                assert im.format == "WEBP" and max(im.size) == 1200  # kichraytirilgan

            bad = await client.post("/api/admin/upload", data={"file": "not an image"}, headers=tma())
            assert bad.status == 400

            new = {"name_uz": "Ayva Lavash", "name_ru": "", "desc_uz": "Tovuq, sous", "price": 35000,
                   "category_id": "burgers", "image": url, "badge": "new"}
            r = await client.post("/api/admin/products", json=new, headers=tma())
            assert r.status == 200, await r.text()
            pid = (await r.json())["product"]["id"]

            boot = await (await client.get("/api/bootstrap", headers=tma(7))).json()
            item = next(p for p in boot["menu"]["products"] if p["id"] == pid)
            assert item["image"] == url and item["name"]["ru"] == "Ayva Lavash" and item["badge"] == "new"
            assert (await client.get(url)).status == 200

            # aksiya: eski narxdan qimmat bo'lsa xato
            r = await client.patch(f"/api/admin/products/{pid}", json={"promo_price": 40000}, headers=tma())
            assert r.status == 400 and (await r.json())["error"] == "promo_not_lower"
            r = await client.patch(f"/api/admin/products/{pid}", json={"promo_price": 28000}, headers=tma())
            assert r.status == 200
            boot = await (await client.get("/api/bootstrap", headers=tma(7))).json()
            item = next(p for p in boot["menu"]["products"] if p["id"] == pid)
            assert (item["price"], item["old_price"], item["discount"]) == (28000, 35000, 20)

            # buyurtmada aksiya narxi ishlatiladi
            order = {**ORDER, "items": [{"id": pid, "qty": 1}], "type": "pickup", "address": "", "lat": None,
                     "lon": None}
            r = await client.post("/api/order", json=order, headers=tma(7))
            assert (await r.json())["order"]["total"] == 28000

            # stop-list va yashirish
            await client.patch(f"/api/admin/products/{pid}", json={"available": False}, headers=tma())
            assert not ctx.catalog.is_available(pid) and ctx.catalog.is_shown(pid)
            await client.patch(f"/api/admin/products/{pid}", json={"visible": False}, headers=tma())
            assert not ctx.catalog.is_shown(pid)

            # noto'g'ri qiymatlar
            for patch in ({"price": -5}, {"badge": "super"}, {"image": "https://evil/x.png"},
                          {"category_id": "nope"}, {"name_uz": ""}, {"promo_from": "2026-12-01", "promo_to": "2026-11-01"}):
                r = await client.patch(f"/api/admin/products/{pid}", json=patch, headers=tma())
                assert r.status == 400, patch

            # o'chirish — rasm fayli ham o'chadi
            assert (await client.delete(f"/api/admin/products/{pid}", headers=tma())).status == 200
            assert not path.exists() and pid not in ctx.catalog.products
        finally:
            await close(client, ctx)
    run(go())


def test_categories_and_reorder(tmp_path):
    async def go():
        client, ctx, _ = await make_client(tmp_path)
        try:
            r = await client.post("/api/admin/categories", json={"name_uz": "Lavashlar", "icon": "wrap"}, headers=tma())
            cid = (await r.json())["category"]["id"]
            assert ctx.catalog.category(cid)["icon"] == "wrap"
            r = await client.delete("/api/admin/categories/burgers", headers=tma())
            assert r.status == 409 and (await r.json())["error"] == "category_not_empty"

            ids = [c["id"] for c in ctx.catalog.categories]
            new_order = [cid] + [i for i in ids if i != cid]
            assert (await client.post("/api/admin/categories/reorder", json={"ids": new_order}, headers=tma())).status == 200
            assert ctx.catalog.categories[0]["id"] == cid
            assert (await client.post("/api/admin/categories/reorder", json={"ids": ["zzz"]}, headers=tma())).status == 400

            await client.patch(f"/api/admin/categories/{cid}", json={"visible": False}, headers=tma())
            boot = await (await client.get("/api/bootstrap", headers=tma(7))).json()
            assert cid not in [c["id"] for c in boot["menu"]["categories"]]
            assert (await client.delete(f"/api/admin/categories/{cid}", headers=tma())).status == 200

            menu = await (await client.get("/api/admin/menu", headers=tma())).json()
            assert len(menu["products"]) == len(ctx.catalog.products) and "wrap" in menu["icons"]
        finally:
            await close(client, ctx)
    run(go())


def test_banners(tmp_path):
    async def go():
        client, ctx, _ = await make_client(tmp_path)
        try:
            r = await client.post("/api/admin/banners", json={"title_uz": "", "image": ""}, headers=tma())
            assert r.status == 400  # sarlavha yoki rasm shart
            body = {"title_uz": "2 ta burger — 1 narxida", "text_uz": "Faqat dushanba", "link_type": "product",
                    "link_id": "classic"}
            r = await client.post("/api/admin/banners", json=body, headers=tma())
            assert r.status == 200, await r.text()
            bid = (await r.json())["banner"]["id"]
            boot = await (await client.get("/api/bootstrap", headers=tma(7))).json()
            assert boot["banners"][0]["link_id"] == "classic"

            await client.patch(f"/api/admin/banners/{bid}", json={"active": False}, headers=tma())
            boot = await (await client.get("/api/bootstrap", headers=tma(7))).json()
            assert boot["banners"] == []
            lst = await (await client.get("/api/admin/banners", headers=tma())).json()
            assert lst["banners"][0]["state"] == "off"
            assert (await client.delete(f"/api/admin/banners/{bid}", headers=tma())).status == 200
        finally:
            await close(client, ctx)
    run(go())


def test_store_settings_and_pause(tmp_path):
    async def go():
        client, ctx, _ = await make_client(tmp_path)
        try:
            r = await client.patch("/api/admin/store", json={"accepting": False}, headers=tma())
            assert r.status == 200
            r = await client.post("/api/order", json=ORDER, headers=tma(7))
            assert r.status == 409 and (await r.json())["error"] == "paused"

            body = {"accepting": True, "delivery": {"fee": 15000}, "payments": {"click": True},
                    "location": {"lat": 41.3, "lon": 69.2}, "support_username": "@ayva_admin"}
            store = (await (await client.patch("/api/admin/store", json=body, headers=tma())).json())["store"]
            assert store["delivery"]["fee"] == 15000 and store["delivery"]["free_from"] == 150000
            assert store["payments"]["click"] is False  # hali ulanmagan
            assert store["support_username"] == "ayva_admin" and store["location"] == {"lat": 41.3, "lon": 69.2}
            assert ctx.catalog.delivery_fee(50000, "delivery") == 15000

            for bad in ({"hours": {"open": "25:00", "close": "02:00"}}, {"name": ""},
                        {"delivery": {"enabled": False}, "pickup": {"enabled": False}},
                        {"payments": {"cash": False}}, {"location": {"lat": 200, "lon": 1}}):
                r = await client.patch("/api/admin/store", json=bad, headers=tma())
                assert r.status == 400, bad
        finally:
            await close(client, ctx)
    run(go())


def test_orders_and_stats(tmp_path):
    async def go():
        client, ctx, session = await make_client(tmp_path)
        try:
            r = await client.post("/api/order", json=ORDER, headers=tma(7))
            oid = (await r.json())["order"]["id"]
            lst = await (await client.get("/api/admin/orders?tab=active", headers=tma())).json()
            assert [o["id"] for o in lst["orders"]] == [oid]

            r = await client.post(f"/api/admin/orders/{oid}/status", json={"status": "done"}, headers=tma())
            assert r.status == 409  # "new" dan to'g'ridan-to'g'ri "done" ga o'tib bo'lmaydi
            for st in ("accepted", "on_the_way", "done"):
                r = await client.post(f"/api/admin/orders/{oid}/status", json={"status": st}, headers=tma())
                assert r.status == 200 and (await r.json())["order"]["status"] == st
            await asyncio.sleep(0.05)
            assert any(type(c).__name__ == "SendMessage" and c.chat_id == 7 for c in session.calls)

            hist = await (await client.get("/api/admin/orders?tab=history", headers=tma())).json()
            assert hist["orders"][0]["id"] == oid
            found = await (await client.get(f"/api/admin/orders?tab=history&q={oid}", headers=tma())).json()
            assert len(found["orders"]) == 1
            by_phone = await (await client.get("/api/admin/orders?tab=history&q=901234", headers=tma())).json()
            assert len(by_phone["orders"]) == 1

            st = await (await client.get("/api/admin/stats?days=7", headers=tma())).json()
            assert st["totals"]["done"] == 1 and st["totals"]["revenue"] == ORDER_TOTAL
            assert st["top"][0]["id"] == "classic" and st["top"][0]["qty"] == 2
            assert len(st["daily"]) == 7 and st["daily"][-1]["revenue"] == ORDER_TOTAL
        finally:
            await close(client, ctx)
    run(go())


ORDER_TOTAL = 32000 * 2 + 10000 + 10000


def test_admins_and_broadcast(tmp_path):
    async def go():
        client, ctx, session = await make_client(tmp_path)
        try:
            r = await client.post("/api/admin/admins", json={"user_id": STRANGER, "name": "Kassir"}, headers=tma())
            assert r.status == 200
            assert (await client.get("/api/admin/me", headers=tma(STRANGER))).status == 200
            # oddiy admin boshqa admin qo'sha olmaydi
            r = await client.post("/api/admin/admins", json={"user_id": 99}, headers=tma(STRANGER))
            assert r.status == 403
            assert (await client.delete(f"/api/admin/admins/{STRANGER}", headers=tma())).status == 200
            assert (await client.get("/api/admin/me", headers=tma(STRANGER))).status == 403

            for uid in (101, 102, 103):
                await ctx.db.upsert_user(uid, "U", None)
            r = await client.post("/api/admin/broadcast", json={"text": "Bugun -20%!", "menu_button": True},
                                  headers=tma())
            assert r.status == 200
            for _ in range(100):
                if not ctx.broadcast["running"]:
                    break
                await asyncio.sleep(0.02)
            assert ctx.broadcast["ok"] == 3
            sent = [c for c in session.calls if type(c).__name__ == "SendMessage"]
            assert sent[0].text == "Bugun -20%!" and sent[0].reply_markup.inline_keyboard[0][0].web_app
            r = await client.post("/api/admin/broadcast", json={"text": ""}, headers=tma())
            assert r.status == 400
        finally:
            await close(client, ctx)
    run(go())
