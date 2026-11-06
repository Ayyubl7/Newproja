"""SQLite ma'lumotlar bazasi (WAL rejimi) — foydalanuvchilar, buyurtmalar, stop-list."""
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

CREATE TABLE IF NOT EXISTS stoplist (
    product_id TEXT PRIMARY KEY
);
"""

# Buyurtma raqamlari 1001 dan boshlansin
FIRST_ORDER_ID = 1001


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
        cur = await self._conn.execute("SELECT seq FROM sqlite_sequence WHERE name='orders'")
        if await cur.fetchone() is None:
            await self._conn.execute(
                "INSERT INTO sqlite_sequence(name, seq) VALUES ('orders', ?)", (FIRST_ORDER_ID - 1,)
            )
        await self._conn.commit()

    async def close(self) -> None:
        if self._conn is not None:
            await self._conn.close()
            self._conn = None

    # ---------- users ----------
    async def upsert_user(self, user_id: int, first_name: str | None, username: str | None) -> None:
        await self.conn.execute(
            """INSERT INTO users(id, first_name, username, created_at) VALUES (?, ?, ?, ?)
               ON CONFLICT(id) DO UPDATE SET first_name=excluded.first_name, username=excluded.username""",
            (user_id, first_name, username, _now()),
        )
        await self.conn.commit()

    async def get_user(self, user_id: int) -> dict[str, Any] | None:
        cur = await self.conn.execute("SELECT * FROM users WHERE id=?", (user_id,))
        row = await cur.fetchone()
        return dict(row) if row else None

    async def set_user_field(self, user_id: int, field: str, value: Any) -> None:
        if field not in ("lang", "phone", "last_address", "first_name"):
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
        cur = await self.conn.execute("SELECT * FROM orders WHERE id=?", (order_id,))
        row = await cur.fetchone()
        return _order_row(row) if row else None

    async def user_orders(self, user_id: int, limit: int = 5) -> list[dict[str, Any]]:
        cur = await self.conn.execute(
            "SELECT * FROM orders WHERE user_id=? ORDER BY id DESC LIMIT ?", (user_id, limit)
        )
        return [_order_row(r) for r in await cur.fetchall()]

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
        cur = await self.conn.execute(
            "SELECT * FROM orders WHERE status IN ('new','accepted','on_the_way','ready') ORDER BY id"
        )
        return [_order_row(r) for r in await cur.fetchall()]

    async def stats_since(self, since_utc: datetime) -> dict[str, int]:
        cur = await self.conn.execute(
            """SELECT
                 COUNT(*)                                             AS total,
                 SUM(status='done')                                   AS done,
                 SUM(status='cancelled')                              AS cancelled,
                 COALESCE(SUM(CASE WHEN status='done' THEN total END), 0) AS revenue
               FROM orders WHERE created_at >= ?""",
            (since_utc.isoformat(timespec="seconds"),),
        )
        row = await cur.fetchone()
        return {k: int(row[k] or 0) for k in ("total", "done", "cancelled", "revenue")}

    # ---------- stoplist ----------
    async def stoplist(self) -> set[str]:
        cur = await self.conn.execute("SELECT product_id FROM stoplist")
        return {r[0] for r in await cur.fetchall()}

    async def toggle_stop(self, product_id: str) -> bool:
        """True qaytarsa — mahsulot endi stop-listda (sotuvda yo'q)."""
        cur = await self.conn.execute("DELETE FROM stoplist WHERE product_id=?", (product_id,))
        if cur.rowcount:
            await self.conn.commit()
            return False
        await self.conn.execute("INSERT INTO stoplist(product_id) VALUES (?)", (product_id,))
        await self.conn.commit()
        return True


def _order_row(row: aiosqlite.Row) -> dict[str, Any]:
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
