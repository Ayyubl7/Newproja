import asyncio
from datetime import date, datetime, timedelta

import pytest

from bot.catalog import TASHKENT_TZ, Catalog, OrderError, fmt_money, promo_active, today_local
from tests.conftest import FIXTURES as DATA_DIR
from bot.db import Database
from bot.seed import ensure_seeded


async def load_catalog(path) -> Catalog:
    db = Database(path)
    await db.connect()
    await ensure_seeded(db, DATA_DIR)
    cat = await Catalog.from_db(db)
    await db.close()
    return cat


@pytest.fixture
def catalog(tmp_path) -> Catalog:
    return asyncio.run(load_catalog(tmp_path / "c.db"))


def at(hh: int, mm: int = 0) -> datetime:
    return datetime(2026, 11, 6, hh, mm, tzinfo=TASHKENT_TZ)


def test_menu_files_are_valid(catalog):
    assert catalog.categories and catalog.products
    for p in catalog.products.values():
        assert p["name"]["uz"] and p["name"]["ru"]


def test_quote_uses_server_prices_and_merges_lines(catalog):
    q = catalog.quote([{"id": "classic", "qty": 1}, {"id": "classic", "qty": 1}, {"id": "fries", "qty": 1}], "delivery")
    assert [(line.product_id, line.qty) for line in q.lines] == [("classic", 2), ("fries", 1)]
    assert q.subtotal == 32000 * 2 + 15000
    assert q.delivery_fee == 10000
    assert q.total == q.subtotal + 10000


def test_free_delivery_threshold(catalog):
    q = catalog.quote([{"id": "combo-friends", "qty": 2}], "delivery")
    assert q.subtotal >= 150000 and q.delivery_fee == 0


def test_pickup_has_no_fee(catalog):
    q = catalog.quote([{"id": "classic", "qty": 1}], "pickup")
    assert q.delivery_fee == 0 and q.total == 32000


@pytest.mark.parametrize("items, code", [
    ([], "empty_cart"),
    ([{"id": "nope", "qty": 1}], "unknown_product"),
    ([{"id": "classic", "qty": 0}], "bad_qty"),
    ([{"id": "classic", "qty": 2.5}], "bad_qty"),
    ([{"id": "classic", "qty": True}], "bad_qty"),
    ([{"id": "classic", "qty": 51}], "bad_qty"),
    ([{"id": "water", "qty": 1}], "min_order"),
    ("classic", "empty_cart"),
])
def test_quote_rejects_bad_input(catalog, items, code):
    with pytest.raises(OrderError) as e:
        catalog.quote(items, "delivery")
    assert e.value.code == code


def test_stoplist_blocks_product(catalog):
    catalog.products["classic"]["available"] = False
    with pytest.raises(OrderError) as e:
        catalog.quote([{"id": "classic", "qty": 3}], "delivery")
    assert e.value.code == "unavailable"
    assert not next(p for p in catalog.public_menu()["products"] if p["id"] == "classic")["available"]


def test_hours_across_midnight(catalog):
    catalog.branches[0]["hours"] = {"open": "10:00", "close": "02:00"}
    assert catalog.is_open(at(10, 0))
    assert catalog.is_open(at(23, 59))
    assert catalog.is_open(at(1, 59))
    assert not catalog.is_open(at(2, 0))
    assert not catalog.is_open(at(9, 59))


def test_hours_same_day(catalog):
    catalog.branches[0]["hours"] = {"open": "09:00", "close": "22:00"}
    assert catalog.is_open(at(12))
    assert not catalog.is_open(at(22, 30))


def test_hidden_product_and_category(catalog):
    catalog.products["fries"]["visible"] = False
    with pytest.raises(OrderError) as e:
        catalog.quote([{"id": "fries", "qty": 3}], "pickup")
    assert e.value.code == "unknown_product"
    next(c for c in catalog.categories if c["id"] == "drinks")["visible"] = False
    menu = catalog.public_menu()
    assert "drinks" not in [c["id"] for c in menu["categories"]]
    assert not any(p["category"] == "drinks" or p["id"] == "fries" for p in menu["products"])


def test_promo_price_used_in_quote_and_menu(catalog):
    p = catalog.products["classic"]
    p["promo_price"] = 24000
    q = catalog.quote([{"id": "classic", "qty": 2}], "pickup")
    assert q.subtotal == 48000
    item = next(i for i in catalog.public_menu()["products"] if i["id"] == "classic")
    assert (item["price"], item["old_price"], item["discount"]) == (24000, 32000, 25)


def test_promo_dates():
    today = date(2026, 11, 6)
    p = {"price": 100, "promo_price": 80, "promo_from": "2026-11-07", "promo_to": None}
    assert not promo_active(p, today)
    p["promo_from"], p["promo_to"] = "2026-11-01", "2026-11-05"
    assert not promo_active(p, today)
    p["promo_to"] = "2026-11-06"
    assert promo_active(p, today)
    p["promo_price"] = 120  # eski narxdan qimmat — aksiya hisoblanmaydi
    assert not promo_active(p, today)


def test_paused_store_is_closed(catalog):
    catalog.branches[0]["hours"] = {"open": "00:00", "close": "00:00"}
    assert catalog.is_open()
    catalog.store["accepting"] = False
    assert not catalog.is_open() and catalog.public_store()["paused"]


def test_banners_respect_dates_and_links(catalog):
    today = today_local()
    base = {"title_uz": "Aksiya", "title_ru": "", "text_uz": "", "text_ru": "", "image": "", "active": 1,
            "link_type": "product", "link_id": "classic", "date_from": None, "date_to": None}
    catalog.banners = [
        {**base, "id": 1},
        {**base, "id": 2, "date_to": (today - timedelta(days=1)).isoformat()},
        {**base, "id": 3, "active": 0},
        {**base, "id": 4, "link_id": "nope"},
    ]
    out = catalog.public_banners()
    assert [b["id"] for b in out] == [1, 4]
    assert out[0]["title"]["ru"] == "Aksiya"  # ruscha bo'sh bo'lsa o'zbekchasi
    assert out[1]["link_type"] == ""  # mavjud bo'lmagan mahsulotga havola o'chiriladi


def test_fmt_money():
    assert fmt_money(125000) == "125 000 so'm"
    assert fmt_money(5000, "ru") == "5 000 сум"


def test_real_menu_seeds_with_variants_and_images(tmp_path):
    from bot.config import DATA_DIR as REAL_DATA, WEBAPP_DIR

    async def go():
        db = Database(tmp_path / "real.db")
        await db.connect()
        await ensure_seeded(db, REAL_DATA)
        cat = await Catalog.from_db(db)
        await db.close()
        return cat

    cat = asyncio.run(go())
    assert len(cat.products) >= 40
    for p in cat.products.values():
        assert p["image"], p["id"]
        assert (WEBAPP_DIR / p["image"]).exists(), p["image"]
        if p["variants"]:
            assert p["price"] == min(v["price"] for v in p["variants"])
    pizza = cat.products["pizza-pepperoni"]
    assert [v["name"]["uz"] for v in pizza["variants"]] == ["Kichik", "O'rta", "Katta"]
    assert cat.store["name"] == "Ayva Burgers"


def test_variants_in_quote_and_menu(tmp_path):
    from bot.config import DATA_DIR as REAL_DATA

    async def go():
        db = Database(tmp_path / "v.db")
        await db.connect()
        await ensure_seeded(db, REAL_DATA)
        cat = await Catalog.from_db(db)
        await db.close()
        return cat

    cat = asyncio.run(go())
    q = cat.quote([{"id": "pizza-pepperoni", "qty": 1, "v": 2}, {"id": "pizza-pepperoni", "qty": 1, "v": 2},
                   {"id": "fries", "qty": 1}], "pickup")
    assert [(line.product_id, line.variant, line.qty, line.price) for line in q.lines] == [
        ("pizza-pepperoni", 2, 2, 70000), ("fries", None, 1, 12000)]
    assert q.lines[0].name["uz"] == "Pepperoni (Katta)" and q.lines[0].as_dict()["v"] == 2
    for bad in ([{"id": "pizza-pepperoni", "qty": 1}], [{"id": "pizza-pepperoni", "qty": 1, "v": 3}],
                [{"id": "fries", "qty": 1, "v": 1}], [{"id": "pizza-pepperoni", "qty": 1, "v": True}]):
        with pytest.raises(OrderError) as e:
            cat.quote(bad, "pickup")
        assert e.value.code == "bad_variant"

    # aksiya foizi har bir variantga qo'llanadi: 45 000 -> 36 000 (-20%), katta 70 000 -> 56 000
    cat.products["pizza-pepperoni"]["promo_price"] = 36000
    q = cat.quote([{"id": "pizza-pepperoni", "qty": 1, "v": 2}], "pickup")
    assert q.subtotal == 56000
    item = next(p for p in cat.public_menu()["products"] if p["id"] == "pizza-pepperoni")
    assert item["price"] == 36000 and item["old_price"] == 45000
    assert [(v["price"], v["old_price"]) for v in item["variants"]] == [(36000, 45000), (48000, 60000), (56000, 70000)]
