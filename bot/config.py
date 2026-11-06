"""Bot sozlamalari: hammasi muhit o'zgaruvchilaridan (.env) olinadi."""
from __future__ import annotations

import os
import secrets
from dataclasses import dataclass
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
WEBAPP_DIR = BASE_DIR / "webapp"


def _load_dotenv(path: Path) -> None:
    """Oddiy .env o'quvchi (qo'shimcha kutubxonasiz). Mavjud o'zgaruvchilarni almashtirmaydi."""
    if not path.exists():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key, value = key.strip(), value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


def _int_set(value: str) -> frozenset[int]:
    out = set()
    for part in value.replace(";", ",").split(","):
        part = part.strip()
        if part.lstrip("-").isdigit():
            out.add(int(part))
    return frozenset(out)


@dataclass(frozen=True)
class Settings:
    bot_token: str
    admin_chat_id: int
    admin_ids: frozenset[int]
    admin_lang: str
    public_url: str
    host: str
    port: int
    db_path: Path
    webhook_secret: str
    mode: str
    dev_mode: bool
    dev_user_id: int

    @property
    def webapp_url(self) -> str:
        return f"{self.public_url}/"

    @property
    def use_webhook(self) -> bool:
        return self.mode == "webhook"

    @property
    def webhook_path(self) -> str:
        # Maxfiy qism URL'da ham turadi — begona so'rovlar webhook'ni topa olmaydi.
        return f"/tg/webhook/{self.webhook_secret[:16]}"


def load_settings() -> Settings:
    _load_dotenv(BASE_DIR / ".env")

    token = os.getenv("BOT_TOKEN", "").strip()
    if not token:
        raise SystemExit("BOT_TOKEN topilmadi. .env faylini to'ldiring (.env.example'ga qarang).")

    public_url = os.getenv("PUBLIC_URL", "").strip().rstrip("/")
    # Railway domenini avtomatik olish
    if not public_url and os.getenv("RAILWAY_PUBLIC_DOMAIN"):
        public_url = f"https://{os.environ['RAILWAY_PUBLIC_DOMAIN']}"

    # auto: https PUBLIC_URL bo'lsa webhook, bo'lmasa polling.
    # web: faqat Mini App serveri (Telegram'ga ulanmaydi) — dizaynni brauzerda ko'rish uchun.
    mode = os.getenv("BOT_MODE", "auto").lower()
    if mode not in ("webhook", "polling", "web"):
        mode = "webhook" if public_url.startswith("https://") else "polling"

    db_path = Path(os.getenv("DB_PATH", str(DATA_DIR / "ayva.db")))
    db_path.parent.mkdir(parents=True, exist_ok=True)

    admin_chat = os.getenv("ADMIN_CHAT_ID", "0").strip()
    admin_lang = os.getenv("ADMIN_LANG", "uz").strip().lower()

    return Settings(
        bot_token=token,
        admin_chat_id=int(admin_chat) if admin_chat.lstrip("-").isdigit() else 0,
        admin_ids=_int_set(os.getenv("ADMIN_IDS", "")),
        admin_lang=admin_lang if admin_lang in ("uz", "ru") else "uz",
        public_url=public_url,
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "8080")),
        db_path=db_path,
        webhook_secret=os.getenv("WEBHOOK_SECRET") or secrets.token_hex(24),
        mode=mode,
        dev_mode=os.getenv("DEV_MODE", "0").lower() in ("1", "true", "yes"),
        dev_user_id=int(os.getenv("DEV_USER_ID", "0") or 0),
    )
