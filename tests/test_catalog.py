from datetime import datetime

import pytest

from bot.catalog import TASHKENT_TZ, Catalog, OrderError, fmt_money
from bot.config import DATA_DIR


@pytest.fixture
def catalog() -> Catalog:
    return Catalog.load(DATA_DIR)


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
    catalog.stoplist.add("classic")
    with pytest.raises(OrderError) as e:
        catalog.quote([{"id": "classic", "qty": 3}], "delivery")
    assert e.value.code == "unavailable"
    assert not next(p for p in catalog.public_menu()["products"] if p["id"] == "classic")["available"]


def test_hours_across_midnight(catalog):
    catalog.store["hours"] = {"open": "10:00", "close": "02:00"}
    assert catalog.is_open(at(10, 0))
    assert catalog.is_open(at(23, 59))
    assert catalog.is_open(at(1, 59))
    assert not catalog.is_open(at(2, 0))
    assert not catalog.is_open(at(9, 59))


def test_hours_same_day(catalog):
    catalog.store["hours"] = {"open": "09:00", "close": "22:00"}
    assert catalog.is_open(at(12))
    assert not catalog.is_open(at(22, 30))


def test_fmt_money():
    assert fmt_money(125000) == "125 000 so'm"
    assert fmt_money(5000, "ru") == "5 000 сум"
