"""SQLite ma'lumotlar bazasi (WAL rejimi): foydalanuvchilar, buyurtmalar, menyu, aksiyalar, sozlamalar."""
from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import aiosqlite

from .catalog import TASHKENT_TZ

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id            INTEGER PRIMARY KEY,
    first_name    TEXT,
    username      TEXT,
    lang          TEXT,
    phone         TEXT,
    last_address  TEXT,
    created_at    TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS orders (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id           INTEGER NOT NULL,
    items             TEXT NOT NULL,
    subtotal          INTEGER NOT NULL,
    delivery_fee      INTEGER NOT NULL,
    total             INTEGER NOT NULL,
    type              TEXT NOT NULL,
    address           TEXT,
    lat               REAL,
    lon               REAL,
    phone             TEXT NOT NULL,
    name              TEXT,
    comment           TEXT,
    payment           TEXT NOT NULL,
    lang              TEXT NOT NULL,
    status            TEXT NOT NULL DEFAULT 'new',
    admin_message_id  INTEGER,
    created_at        TEXT NOT NULL,
    updated_at        TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_orders_user ON orders(user_id, id DESC);
CREATE INDEX IF NOT EXISTS idx_orders_created ON orders(created_at);
CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);

-- eski versiyadan qolgan (migratsiyada products.available ga o'tkaziladi)
CREATE TABLE IF NOT EXISTS stoplist (
    product_id TEXT PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS categories (
    id       TEXT PRIMARY KEY,
    name_uz  TEXT NOT NULL,
    name_ru  TEXT NOT NULL DEFAULT '',
    icon     TEXT NOT NULL DEFAULT 'burger',
    sort     INTEGER NOT NULL DEFAULT 0,
    visible  INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS products (
    id           TEXT PRIMARY KEY,
    category_id  TEXT NOT NULL,
    name_uz      TEXT NOT NULL,
    name_ru      TEXT NOT NULL DEFAULT '',
    desc_uz      TEXT NOT NULL DEFAULT '',
    desc_ru      TEXT NOT NULL DEFAULT '',
    price        INTEGER NOT NULL,
    promo_price  INTEGER,
    promo_from   TEXT,
    promo_to     TEXT,
    image        TEXT NOT NULL DEFAULT '',
    badge        TEXT NOT NULL DEFAULT '',
    available    INTEGER NOT NULL DEFAULT 1,
    visible      INTEGER NOT NULL DEFAULT 1,
    sort         INTEGER NOT NULL DEFAULT 0,
    variants     TEXT,
    created_at   TEXT NOT NULL,
    updated_at   TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_products_cat ON products(category_id, sort);

CREATE TABLE IF NOT EXISTS banners (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    title_uz   TEXT NOT NULL DEFAULT '',
    title_ru   TEXT NOT NULL DEFAULT '',
    text_uz    TEXT NOT NULL DEFAULT '',
    text_ru    TEXT NOT NULL DEFAULT '',
    image      TEXT NOT NULL DEFAULT '',
    link_type  TEXT NOT NULL DEFAULT '',
    link_id    TEXT NOT NULL DEFAULT '',
    date_from  TEXT,
    date_to    TEXT,
    active     INTEGER NOT NULL DEFAULT 1,
    sort       INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS settings (
    key    TEXT PRIMARY KEY,
    value  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS admins (
    user_id    INTEGER PRIMARY KEY,
    name       TEXT NOT NULL DEFAULT '',
    role       TEXT NOT NULL DEFAULT 'admin',
    created_at TEXT NOT NULL
);
"""

# Buyurtma raqamlari 1001 dan boshlansin
FIRST_ORDER_ID = 1001

CATEGORY_FIELDS = ("name_uz", "name_ru", "icon", "sort", "visible")
PRODUCT_FIELDS = (
    "category_id", "name_uz", "name_ru", "desc_uz", "desc_ru", "price", "promo_price", "promo_from",
    "promo_to", "image", "badge", "available", "visible", "sort", "variants",
)
BANNER_FIELDS = (
    "title_uz", "title_ru", "text_uz", "text_ru", "image", "link_type", "link_id",
    "date_from", "date_to", "active", "sort",
)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class Database:
    def __init__(self, path: Path) -> None:
        self.path = path
        self._conn: aiosqlite.Connection | None = None

    @property
    def conn(self) -> aiosqlite.Connection:
        if self._conn is None:
            raise RuntimeError("Database.connect() chaqirilmagan")
        return self._conn

    async def connect(self) -> None:
        self._conn = await aiosqlite.connect(self.path)
        self._conn.row_factory = aiosqlite.Row
        await self._conn.execute("PRAGMA journal_mode=WAL")
        await self._conn.execute("PRAGMA synchronous=NORMAL")
        await self._conn.execute("PRAGMA busy_timeout=5000")
        await self._conn.executescript(SCHEMA)
        await self._migrate()
        cur = await self._conn.execute("SELECT seq FROM sqlite_sequence WHERE name='orders'")
        if await cur.fetchone() is None:
            await self._conn.execute(
                "INSERT INTO sqlite_sequence(name, seq) VALUES ('orders', ?)", (FIRST_ORDER_ID - 1,)
            )
        await self._conn.commit()

    async def _migrate(self) -> None:
        """Eski bazalarga yangi ustunlarni qo'shish."""
        cur = await self.conn.execute("PRAGMA table_info(admins)")
        if "role" not in {r[1] for r in await cur.fetchall()}:
            await self.conn.execute("ALTER TABLE admins ADD COLUMN role TEXT NOT NULL DEFAULT 'admin'")
        cur = await self.conn.execute("PRAGMA table_info(products)")
        if "variants" not in {r[1] for r in await cur.fetchall()}:
            await self.conn.execute("ALTER TABLE products ADD COLUMN variants TEXT")
        cur = await self.conn.execute("PRAGMA table_info(users)")
        user_cols = {r[1] for r in await cur.fetchall()}
        for col, decl in (("last_lat", "REAL"), ("last_lon", "REAL"), ("pref_type", "TEXT")):
            if col not in user_cols:
                await self.conn.execute(f"ALTER TABLE users ADD COLUMN {col} {decl}")

    async def close(self) -> None:
        if self._conn is not None:
            await self._conn.close()
            self._conn = None

    async def _all(self, sql: str, params: tuple = ()) -> list[dict[str, Any]]:
        cur = await self.conn.execute(sql, params)
        return [dict(r) for r in await cur.fetchall()]

    async def _one(self, sql: str, params: tuple = ()) -> dict[str, Any] | None:
        cur = await self.conn.execute(sql, params)
        row = await cur.fetchone()
        return dict(row) if row else None

    # ---------- users ----------
    async def upsert_user(self, user_id: int, first_name: str | None, username: str | None) -> None:
        await self.conn.execute(
            """INSERT INTO users(id, first_name, username, created_at) VALUES (?, ?, ?, ?)
               ON CONFLICT(id) DO UPDATE SET first_name=excluded.first_name, username=excluded.username""",
            (user_id, first_name, username, _now()),
        )
        await self.conn.commit()

    async def get_user(self, user_id: int) -> dict[str, Any] | None:
        return await self._one("SELECT * FROM users WHERE id=?", (user_id,))

    async def set_user_field(self, user_id: int, field: str, value: Any) -> None:
        if field not in ("lang", "phone", "last_address", "first_name", "last_lat", "last_lon", "pref_type"):
            raise ValueError(field)
        await self.conn.execute(
            f"INSERT INTO users(id, {field}, created_at) VALUES (?, ?, ?) "
            f"ON CONFLICT(id) DO UPDATE SET {field}=excluded.{field}",
            (user_id, value, _now()),
        )
        await self.conn.commit()

    async def all_user_ids(self) -> list[int]:
        cur = await self.conn.execute("SELECT id FROM users")
        return [r[0] for r in await cur.fetchall()]

    async def set_location(self, user_id: int, lat: float, lon: float, address: str) -> None:
        await self.conn.execute(
            "INSERT INTO users(id, last_lat, last_lon, last_address, pref_type, created_at) VALUES (?, ?, ?, ?, 'delivery', ?) "
            "ON CONFLICT(id) DO UPDATE SET last_lat=excluded.last_lat, last_lon=excluded.last_lon, "
            "last_address=excluded.last_address, pref_type='delivery'",
            (user_id, lat, lon, address, _now()),
        )
        await self.conn.commit()

    async def all_users_lang(self) -> list[tuple[int, str | None]]:
        cur = await self.conn.execute("SELECT id, lang FROM users")
        return [(r[0], r[1]) for r in await cur.fetchall()]

    async def users_by_ids(self, ids: list[int]) -> dict[int, dict[str, Any]]:
        if not ids:
            return {}
        rows = await self._all(f"SELECT * FROM users WHERE id IN ({','.join('?' * len(ids))})", tuple(ids))
        return {r["id"]: r for r in rows}

    async def count_users_since(self, since_utc: datetime) -> int:
        cur = await self.conn.execute("SELECT COUNT(*) FROM users WHERE created_at >= ?",
                                      (since_utc.isoformat(timespec="seconds"),))
        return int((await cur.fetchone())[0])

    # ---------- orders ----------
    async def create_order(self, data: dict[str, Any]) -> int:
        now = _now()
        cur = await self.conn.execute(
            """INSERT INTO orders(user_id, items, subtotal, delivery_fee, total, type, address, lat, lon,
                                  phone, name, comment, payment, lang, status, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'new', ?, ?)""",
            (
                data["user_id"], json.dumps(data["items"], ensure_ascii=False), data["subtotal"],
                data["delivery_fee"], data["total"], data["type"], data.get("address"),
                data.get("lat"), data.get("lon"), data["phone"], data.get("name"),
                data.get("comment"), data["payment"], data["lang"], now, now,
            ),
        )
        await self.conn.commit()
        return int(cur.lastrowid)

    async def get_order(self, order_id: int) -> dict[str, Any] | None:
        row = await self._one("SELECT * FROM orders WHERE id=?", (order_id,))
        return _order_row(row) if row else None

    async def user_orders(self, user_id: int, limit: int = 5) -> list[dict[str, Any]]:
        rows = await self._all("SELECT * FROM orders WHERE user_id=? ORDER BY id DESC LIMIT ?", (user_id, limit))
        return [_order_row(r) for r in rows]

    async def update_status(self, order_id: int, expected: str, new: str) -> bool:
        """Holatni faqat kutilgan holatdan o'zgartiradi (ikki admin bir vaqtda bossa ham to'g'ri ishlaydi)."""
        cur = await self.conn.execute(
            "UPDATE orders SET status=?, updated_at=? WHERE id=? AND status=?",
            (new, _now(), order_id, expected),
        )
        await self.conn.commit()
        return cur.rowcount == 1

    async def set_admin_message(self, order_id: int, message_id: int) -> None:
        await self.conn.execute("UPDATE orders SET admin_message_id=? WHERE id=?", (message_id, order_id))
        await self.conn.commit()

    async def active_orders(self) -> list[dict[str, Any]]:
        rows = await self._all(
            "SELECT * FROM orders WHERE status IN ('new','accepted','on_the_way','ready') ORDER BY id"
        )
        return [_order_row(r) for r in rows]

    async def search_orders(self, statuses: tuple[str, ...], query: str = "", before_id: int | None = None,
                            limit: int = 30) -> list[dict[str, Any]]:
        where = [f"status IN ({','.join('?' * len(statuses))})"]
        params: list[Any] = list(statuses)
        if query:
            digits = "".join(c for c in query if c.isdigit())
            phone_sql = "REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(phone,' ',''),'-',''),'+',''),'(',''),')','') LIKE ?"
            if query.startswith("#") and digits:
                where.append("id = ?")
                params.append(int(digits))
            elif query.isdigit() and len(query) <= 7:
                # qisqa raqam — buyurtma raqami ham, telefon bo'lagi ham bo'lishi mumkin
                where.append(f"(id = ? OR {phone_sql})")
                params += [int(query), f"%{digits}%"]
            elif digits:
                where.append(phone_sql)
                params.append(f"%{digits}%")
            else:
                where.append("name LIKE ?")
                params.append(f"%{query}%")
        if before_id:
            where.append("id < ?")
            params.append(before_id)
        params.append(limit)
        rows = await self._all(f"SELECT * FROM orders WHERE {' AND '.join(where)} ORDER BY id DESC LIMIT ?",
                               tuple(params))
        return [_order_row(r) for r in rows]

    async def orders_since(self, since_utc: datetime) -> list[dict[str, Any]]:
        rows = await self._all("SELECT * FROM orders WHERE created_at >= ? ORDER BY id",
                               (since_utc.isoformat(timespec="seconds"),))
        return [_order_row(r) for r in rows]

    async def stats_since(self, since_utc: datetime) -> dict[str, int]:
        row = await self._one(
            """SELECT
                 COUNT(*)                                             AS total,
                 SUM(status='done')                                   AS done,
                 SUM(status='cancelled')                              AS cancelled,
                 COALESCE(SUM(CASE WHEN status='done' THEN total END), 0) AS revenue
               FROM orders WHERE created_at >= ?""",
            (since_utc.isoformat(timespec="seconds"),),
        )
        return {k: int(row[k] or 0) for k in ("total", "done", "cancelled", "revenue")}

    # ---------- categories ----------
    async def list_categories(self) -> list[dict[str, Any]]:
        return await self._all("SELECT * FROM categories ORDER BY sort, rowid")

    async def get_category(self, cat_id: str) -> dict[str, Any] | None:
        return await self._one("SELECT * FROM categories WHERE id=?", (cat_id,))

    async def create_category(self, cat_id: str, data: dict[str, Any]) -> None:
        cur = await self.conn.execute("SELECT COALESCE(MAX(sort), -1) + 1 FROM categories")
        sort = data.get("sort", (await cur.fetchone())[0])
        await self.conn.execute(
            "INSERT INTO categories(id, name_uz, name_ru, icon, sort, visible) VALUES (?, ?, ?, ?, ?, ?)",
            (cat_id, data["name_uz"], data.get("name_ru", ""), data.get("icon", "burger"), sort,
             int(data.get("visible", 1))),
        )
        await self.conn.commit()

    async def update_category(self, cat_id: str, data: dict[str, Any]) -> None:
        await self._update("categories", "id", cat_id, data, CATEGORY_FIELDS)

    async def delete_category(self, cat_id: str) -> None:
        await self.conn.execute("DELETE FROM categories WHERE id=?", (cat_id,))
        await self.conn.commit()

    async def count_products_in(self, cat_id: str) -> int:
        cur = await self.conn.execute("SELECT COUNT(*) FROM products WHERE category_id=?", (cat_id,))
        return int((await cur.fetchone())[0])

    # ---------- products ----------
    async def list_products(self) -> list[dict[str, Any]]:
        return await self._all(
            """SELECT p.* FROM products p LEFT JOIN categories c ON c.id = p.category_id
               ORDER BY COALESCE(c.sort, 1e9), p.sort, p.rowid"""
        )

    async def get_product(self, product_id: str) -> dict[str, Any] | None:
        return await self._one("SELECT * FROM products WHERE id=?", (product_id,))

    async def create_product(self, product_id: str, data: dict[str, Any]) -> None:
        now = _now()
        if "sort" not in data:
            cur = await self.conn.execute("SELECT COALESCE(MAX(sort), -1) + 1 FROM products WHERE category_id=?",
                                          (data["category_id"],))
            data = {**data, "sort": (await cur.fetchone())[0]}
        cols = [f for f in PRODUCT_FIELDS if f in data]
        await self.conn.execute(
            f"INSERT INTO products(id, {', '.join(cols)}, created_at, updated_at) "
            f"VALUES (?, {', '.join('?' * len(cols))}, ?, ?)",
            (product_id, *[_db_value(data[c]) for c in cols], now, now),
        )
        await self.conn.commit()

    async def update_product(self, product_id: str, data: dict[str, Any]) -> None:
        await self._update("products", "id", product_id, data, PRODUCT_FIELDS, touch=True)

    async def delete_product(self, product_id: str) -> None:
        await self.conn.execute("DELETE FROM products WHERE id=?", (product_id,))
        await self.conn.commit()

    async def reorder(self, table: str, ids: list[Any]) -> None:
        if table not in ("categories", "products", "banners"):
            raise ValueError(table)
        await self.conn.executemany(f"UPDATE {table} SET sort=? WHERE id=?", [(i, v) for i, v in enumerate(ids)])
        await self.conn.commit()

    async def image_in_use(self, image: str) -> bool:
        cur = await self.conn.execute(
            "SELECT (SELECT COUNT(*) FROM products WHERE image=?) + (SELECT COUNT(*) FROM banners WHERE image=?)",
            (image, image),
        )
        return int((await cur.fetchone())[0]) > 0

    # ---------- banners ----------
    async def list_banners(self) -> list[dict[str, Any]]:
        return await self._all("SELECT * FROM banners ORDER BY sort, id")

    async def get_banner(self, banner_id: int) -> dict[str, Any] | None:
        return await self._one("SELECT * FROM banners WHERE id=?", (banner_id,))

    async def create_banner(self, data: dict[str, Any]) -> int:
        cur = await self.conn.execute("SELECT COALESCE(MAX(sort), -1) + 1 FROM banners")
        data = {**data, "sort": data.get("sort", (await cur.fetchone())[0])}
        cols = [f for f in BANNER_FIELDS if f in data]
        cur = await self.conn.execute(
            f"INSERT INTO banners({', '.join(cols)}, created_at) VALUES ({', '.join('?' * len(cols))}, ?)",
            (*[_db_value(data[c]) for c in cols], _now()),
        )
        await self.conn.commit()
        return int(cur.lastrowid)

    async def update_banner(self, banner_id: int, data: dict[str, Any]) -> None:
        await self._update("banners", "id", banner_id, data, BANNER_FIELDS)

    async def delete_banner(self, banner_id: int) -> None:
        await self.conn.execute("DELETE FROM banners WHERE id=?", (banner_id,))
        await self.conn.commit()

    # ---------- settings ----------
    async def get_setting(self, key: str) -> Any:
        row = await self._one("SELECT value FROM settings WHERE key=?", (key,))
        return json.loads(row["value"]) if row else None

    async def set_setting(self, key: str, value: Any) -> None:
        await self.conn.execute(
            "INSERT INTO settings(key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
            (key, json.dumps(value, ensure_ascii=False)),
        )
        await self.conn.commit()

    # ---------- admins ----------
    async def list_admins(self) -> list[dict[str, Any]]:
        return await self._all("SELECT * FROM admins ORDER BY created_at")

    async def add_admin(self, user_id: int, name: str, role: str = "admin") -> None:
        await self.conn.execute(
            "INSERT INTO admins(user_id, name, role, created_at) VALUES (?, ?, ?, ?) "
            "ON CONFLICT(user_id) DO UPDATE SET name=excluded.name, role=excluded.role",
            (user_id, name, role, _now()),
        )
        await self.conn.commit()

    async def remove_admin(self, user_id: int) -> None:
        await self.conn.execute("DELETE FROM admins WHERE user_id=?", (user_id,))
        await self.conn.commit()

    # ---------- legacy stoplist ----------
    async def pop_legacy_stoplist(self) -> set[str]:
        cur = await self.conn.execute("SELECT product_id FROM stoplist")
        ids = {r[0] for r in await cur.fetchall()}
        if ids:
            await self.conn.execute("DELETE FROM stoplist")
            await self.conn.commit()
        return ids

    # ---------- helpers ----------
    async def _update(self, table: str, key: str, key_value: Any, data: dict[str, Any],
                      allowed: tuple[str, ...], touch: bool = False) -> None:
        cols = [c for c in allowed if c in data]
        if not cols:
            return
        sets = ", ".join(f"{c}=?" for c in cols)
        params = [_db_value(data[c]) for c in cols]
        if touch:
            sets += ", updated_at=?"
            params.append(_now())
        await self.conn.execute(f"UPDATE {table} SET {sets} WHERE {key}=?", (*params, key_value))
        await self.conn.commit()


def _db_value(v: Any) -> Any:
    if isinstance(v, bool):
        return int(v)
    if isinstance(v, (list, dict)):
        return json.dumps(v, ensure_ascii=False) if v else None
    return v


def _order_row(row: dict[str, Any]) -> dict[str, Any]:
    d = dict(row)
    d["items"] = json.loads(d["items"])
    return d


def local_time(iso_utc: str) -> datetime:
    return datetime.fromisoformat(iso_utc).astimezone(TASHKENT_TZ)


def start_of_today_utc() -> datetime:
    now = datetime.now(TASHKENT_TZ)
    start_local = now.replace(hour=0, minute=0, second=0, microsecond=0)
    return start_local.astimezone(timezone.utc)


def days_ago_utc(days: int) -> datetime:
    return start_of_today_utc() - timedelta(days=days)
